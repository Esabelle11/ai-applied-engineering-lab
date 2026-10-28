"""Small tts.ai adapter and MP3 assembly helpers.

The adapter implements the documented submit -> poll -> download flow used by
the reference project. It does not make calls at import time and never logs
the API key or returned signed download URL.
"""

from __future__ import annotations

import math
import subprocess
import tempfile
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol
from urllib.parse import urlparse

from applied_ai.core.exceptions import (
    AuthenticationError,
    ConfigurationError,
    InvalidRequestError,
    ProviderConnectionError,
    ProviderResponseError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    RateLimitError,
)

if TYPE_CHECKING:
    import httpx


DEFAULT_TTS_AI_URL = "https://api.tts.ai/v1"


def _httpx() -> Any:
    try:
        import httpx
    except ImportError as exc:
        raise ConfigurationError("TTS needs httpx: uv sync --extra providers") from exc
    return httpx


@dataclass(frozen=True, slots=True)
class SynthesizedSpeech:
    """One MP3 segment returned by a speech provider."""

    mp3: bytes
    voice: str


class SpeechSynthesizer(Protocol):
    def synthesize(self, text: str, voice: str) -> SynthesizedSpeech: ...


@dataclass(frozen=True, slots=True)
class SpeechSegment:
    speaker: str
    text: str


@dataclass(frozen=True, slots=True)
class AudioTimelineEntry:
    speaker: str
    start_seconds: float
    end_seconds: float

    @property
    def duration_seconds(self) -> float:
        return self.end_seconds - self.start_seconds


@dataclass(frozen=True, slots=True)
class RenderedMP3:
    mp3: bytes
    duration_seconds: float
    timeline: tuple[AudioTimelineEntry, ...]


class TtsAiProvider:
    """Synchronous tts.ai Kokoro client with bounded status polling."""

    def __init__(
        self,
        *,
        api_key: str | None,
        base_url: str = DEFAULT_TTS_AI_URL,
        timeout_seconds: float = 30.0,
        max_polls: int = 30,
        poll_interval_seconds: float = 1.2,
        client: httpx.Client | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        key = (api_key or "").strip()
        if not key:
            raise ConfigurationError("TTS_AI_KEY is required to synthesize audio")
        parsed = urlparse(base_url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError("TTS base_url must use HTTPS")
        if not 0 < timeout_seconds <= 600:
            raise ValueError("timeout_seconds must be in (0, 600]")
        if max_polls < 1 or poll_interval_seconds < 0:
            raise ValueError(
                "max_polls must be positive and poll_interval_seconds cannot be negative"
            )
        httpx_module = _httpx()
        self._key = key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds
        self._max_polls = max_polls
        self._poll_interval = poll_interval_seconds
        self._httpx = httpx_module
        self._owns_client = client is None
        self._client = client if client is not None else httpx_module.Client()
        self._sleep = sleep

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> TtsAiProvider:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def synthesize(self, text: str, voice: str) -> SynthesizedSpeech:
        """Submit text, wait for completion, and download exactly one MP3 segment."""
        if not text.strip() or not voice.strip():
            raise ValueError("TTS text and voice must be non-empty")
        payload = self._post_json(
            f"{self._base_url}/tts/",
            {"model": "kokoro", "text": text.strip(), "voice": voice.strip(), "format": "mp3"},
        )
        result_url = self._result_url(payload)
        if result_url is None:
            job_id = _required_string(payload, "uuid", "TTS submit response")
            result_url = self._poll(job_id)
        return SynthesizedSpeech(self._download_mp3(result_url), voice.strip())

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._key}", "Content-Type": "application/json"}

    def _post_json(self, url: str, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        try:
            response = self._client.post(
                url, headers=self._headers(), json=dict(payload), timeout=self._timeout
            )
        except self._httpx.TimeoutException as exc:
            raise ProviderTimeoutError("TTS request timed out", provider="tts.ai") from exc
        except self._httpx.RequestError as exc:
            raise ProviderConnectionError("Unable to connect to tts.ai", provider="tts.ai") from exc
        return self._json_response(response, "TTS submit")

    def _poll(self, job_id: str) -> str:
        for attempt in range(self._max_polls):
            try:
                response = self._client.get(
                    f"{self._base_url}/speech/results/",
                    params={"uuid": job_id},
                    headers=self._headers(),
                    timeout=self._timeout,
                )
            except self._httpx.TimeoutException as exc:
                raise ProviderTimeoutError("TTS status poll timed out", provider="tts.ai") from exc
            except self._httpx.RequestError as exc:
                raise ProviderConnectionError("Unable to poll tts.ai", provider="tts.ai") from exc
            payload = self._json_response(response, "TTS status")
            status = _required_string(payload, "status", "TTS status response").lower()
            result_url = self._result_url(payload)
            if status == "completed" and result_url is not None:
                return result_url
            if status == "failed":
                raise ProviderResponseError("TTS job failed", provider="tts.ai")
            if attempt + 1 < self._max_polls:
                self._sleep(self._poll_interval)
        raise ProviderTimeoutError(
            "TTS job did not complete before polling limit", provider="tts.ai"
        )

    def _download_mp3(self, result_url: str) -> bytes:
        parsed = urlparse(result_url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ProviderResponseError("TTS returned an unsafe audio URL", provider="tts.ai")
        try:
            response = self._client.get(result_url, timeout=self._timeout)
        except self._httpx.TimeoutException as exc:
            raise ProviderTimeoutError("TTS audio download timed out", provider="tts.ai") from exc
        except self._httpx.RequestError as exc:
            raise ProviderConnectionError(
                "Unable to download TTS audio", provider="tts.ai"
            ) from exc
        self._raise_for_status(response, "TTS audio download")
        audio = response.content
        if not isinstance(audio, bytes) or not audio:
            raise ProviderResponseError("TTS returned empty audio", provider="tts.ai")
        return audio

    def _json_response(self, response: Any, operation: str) -> Mapping[str, Any]:
        self._raise_for_status(response, operation)
        try:
            payload = response.json()
        except (ValueError, UnicodeError) as exc:
            raise ProviderResponseError(
                f"{operation} returned invalid JSON", provider="tts.ai"
            ) from exc
        if not isinstance(payload, Mapping):
            raise ProviderResponseError(
                f"{operation} returned a non-object response", provider="tts.ai"
            )
        return payload

    def _raise_for_status(self, response: Any, operation: str) -> None:
        status = response.status_code
        if status < 400:
            return
        request_id = response.headers.get("x-request-id") or response.headers.get("request-id")
        details = {"provider": "tts.ai", "status_code": status, "request_id": request_id}
        if status == 401:
            raise AuthenticationError(f"{operation} authentication failed", **details)
        if status == 429:
            raise RateLimitError(f"{operation} was rate limited", **details)
        if status in {408, 504}:
            raise ProviderTimeoutError(f"{operation} timed out", **details)
        if status == 409 or status >= 500:
            raise ProviderUnavailableError(f"{operation} is unavailable", **details)
        raise InvalidRequestError(f"{operation} was rejected", **details)

    @staticmethod
    def _result_url(payload: Mapping[str, Any]) -> str | None:
        value = payload.get("result_url")
        return value.strip() if isinstance(value, str) and value.strip() else None


def _required_string(payload: Mapping[str, Any], key: str, label: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ProviderResponseError(f"{label} needs a non-empty {key}", provider="tts.ai")
    return value.strip()


def mp3_duration_seconds(mp3: bytes) -> float:
    """Measure a single MP3 with ffprobe, avoiding shell interpolation and temp-file leaks."""
    if not mp3:
        raise ValueError("Cannot measure empty MP3 data")
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temporary_file:
            temporary_file.write(mp3)
            temporary_path = Path(temporary_file.name)
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(temporary_path),
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    except FileNotFoundError as exc:
        raise ConfigurationError("ffprobe is required to measure generated MP3 audio") from exc
    except subprocess.TimeoutExpired as exc:
        raise ProviderTimeoutError(
            "ffprobe timed out while measuring MP3", provider="local-audio"
        ) from exc
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
    if result.returncode != 0:
        raise ProviderResponseError("ffprobe could not read generated MP3", provider="local-audio")
    try:
        duration = float(result.stdout.strip())
    except ValueError as exc:
        raise ProviderResponseError(
            "ffprobe returned an invalid MP3 duration", provider="local-audio"
        ) from exc
    if not math.isfinite(duration) or duration <= 0:
        raise ProviderResponseError(
            "ffprobe returned a non-positive MP3 duration", provider="local-audio"
        )
    return duration


def render_mp3_segments(
    segments: Sequence[SpeechSegment],
    *,
    voices: Mapping[str, str],
    synthesizer: SpeechSynthesizer,
    duration_reader: Callable[[bytes], float] = mp3_duration_seconds,
) -> RenderedMP3:
    """Synthesize ordered transcript lines and join same-format MP3 frames in order."""
    if not segments:
        raise ValueError("At least one transcript segment is required")
    chunks: list[bytes] = []
    timeline: list[AudioTimelineEntry] = []
    current_time = 0.0
    for index, segment in enumerate(segments, start=1):
        voice = voices.get(segment.speaker)
        if not voice:
            raise ValueError(f"No voice is configured for transcript speaker {segment.speaker!r}")
        speech = synthesizer.synthesize(segment.text, voice)
        if not speech.mp3:
            raise ProviderResponseError(
                f"TTS returned empty audio for segment {index}", provider="tts.ai"
            )
        duration = duration_reader(speech.mp3)
        if not math.isfinite(duration) or duration <= 0:
            raise ValueError(f"Segment {index} has an invalid audio duration")
        chunks.append(speech.mp3)
        end_time = current_time + duration
        timeline.append(AudioTimelineEntry(segment.speaker, current_time, end_time))
        current_time = end_time
    return RenderedMP3(b"".join(chunks), current_time, tuple(timeline))


def write_mp3(path: Path, rendered: RenderedMP3, *, overwrite: bool = False) -> Path:
    """Persist rendered MP3 data only when the caller explicitly allows replacement."""
    if path.suffix.lower() != ".mp3":
        raise ValueError("Audio output path must end in .mp3")
    if path.exists() and not overwrite:
        raise FileExistsError(f"Audio output already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(rendered.mp3)
    return path
