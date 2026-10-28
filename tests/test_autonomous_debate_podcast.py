from __future__ import annotations

import pytest

from applied_ai.core import LLMResponse
from applied_ai.media.tts import SynthesizedSpeech, TtsAiProvider
from case_studies.autonomous_debate.run import (
    LIVE_SCHEDULE,
    _load_research,
    generate_live_debate,
    main,
    replay,
    synthesize_episode_audio,
)


def test_replay_loads_the_selected_episode_and_audio() -> None:
    result = replay()

    assert result.provider == "replay"
    assert result.research.title == "Disk Polishing Goes Open Source - Hackaday"
    assert result.audio is not None and result.audio.path.is_file()
    assert result.audio.duration_seconds > 0
    assert len(result.transcript) == 15
    assert result.transcript[0].speaker == "Marcus"
    assert result.transcript[-1].speaker == "Marcus"


def test_live_director_uses_the_fixed_schedule_and_only_seven_calls() -> None:
    class FakeProvider:
        name = "fake"

        def __init__(self) -> None:
            self.requests = []

        def generate(self, request: object) -> LLMResponse:
            self.requests.append(request)
            return LLMResponse("A bounded response.", "fake-model", self.name)

    provider = FakeProvider()
    result = generate_live_debate(provider, "fake-model", _load_research())

    assert len(provider.requests) == len(LIVE_SCHEDULE) == 7
    assert tuple(turn.speaker for turn in result.transcript) == tuple(
        instruction.speaker for instruction in LIVE_SCHEDULE
    )
    assert result.audio is None


def test_audio_renderer_uses_the_configured_voice_for_each_replay_speaker(tmp_path) -> None:
    class FakeSynthesizer:
        def __init__(self) -> None:
            self.calls: list[tuple[str, str]] = []

        def synthesize(self, text: str, voice: str) -> SynthesizedSpeech:
            self.calls.append((text, voice))
            return SynthesizedSpeech(text.encode("utf-8"), voice)

    synthesizer = FakeSynthesizer()
    result = synthesize_episode_audio(
        replay(),
        output_path=tmp_path / "debate.mp3",
        synthesizer=synthesizer,
        duration_reader=lambda _mp3: 1.5,
    )

    assert result.audio is not None
    assert result.audio.path.read_bytes()
    assert len(result.audio.timeline) == len(result.transcript)
    assert [voice for _, voice in synthesizer.calls] == [
        {"Marcus": "am_adam", "Alex": "bm_george", "Sarah": "af_bella"}[turn.speaker]
        for turn in result.transcript
    ]


def test_tts_provider_polls_then_downloads_completed_audio() -> None:
    class Response:
        def __init__(self, *, payload=None, content: bytes = b"") -> None:
            self.status_code = 200
            self.headers = {}
            self._payload = payload
            self.content = content

        def json(self):
            return self._payload

    class Client:
        def __init__(self) -> None:
            self.get_urls: list[str] = []

        def post(self, *_args, **_kwargs) -> Response:
            return Response(payload={"status": "queued", "uuid": "job-123"})

        def get(self, url: str, **_kwargs) -> Response:
            self.get_urls.append(url)
            if url.endswith("/speech/results/"):
                return Response(
                    payload={"status": "completed", "result_url": "https://cdn.tts.ai/job.mp3"}
                )
            return Response(content=b"mp3-bytes")

    client = Client()
    provider = TtsAiProvider(
        api_key="test-key",
        client=client,  # type: ignore[arg-type]
        poll_interval_seconds=0,
    )

    result = provider.synthesize("Hello", "am_adam")

    assert result.mp3 == b"mp3-bytes"
    assert result.voice == "am_adam"
    assert client.get_urls == [
        "https://api.tts.ai/v1/speech/results/",
        "https://cdn.tts.ai/job.mp3",
    ]


def test_replay_rejects_redundant_tts_synthesis(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit, match="2"):
        main(["--replay", "--synthesize-audio"])

    assert "--replay already includes captured audio" in capsys.readouterr().err
