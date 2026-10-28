from __future__ import annotations

import argparse
import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from types import MappingProxyType
from typing import Any

from applied_ai.core import ConfigurationError, LLMProvider, LLMRequest, Message
from applied_ai.media import (
    AudioTimelineEntry,
    SpeechSegment,
    SpeechSynthesizer,
    TtsAiProvider,
    render_mp3_segments,
    write_mp3,
)
from applied_ai.providers.factory import ProviderFactory

DATA_DIR = Path(__file__).resolve().parent / "data"
RESEARCH_PATH = DATA_DIR / "research_disk_polishing_replay.json"
EPISODE_PATH = DATA_DIR / "episode_replay.json"
AUDIO_PATH = DATA_DIR / "18ad16d6-8341-4b76-bb61-ed65ef4a1a94.mp3"

PHASE_ORDER = ("OPENING", "BUILD", "CLASH", "CONSOLIDATION", "CLOSING")
REPLAY_SPEAKERS = ("Marcus", "Sarah", "Alex")


@dataclass(frozen=True, slots=True)
class ResearchBrief:
    """The reviewed source record; this example intentionally does no web research."""

    title: str
    source: str
    published_at: str
    facts: tuple[str, ...]
    topic: str
    background: str


@dataclass(frozen=True, slots=True)
class DebateTurn:
    speaker: str
    text: str
    phase: str


@dataclass(frozen=True, slots=True)
class AudioArtifact:
    """A local recording and the measured, speaker-level timing metadata."""

    path: Path
    duration_seconds: float
    timeline: tuple[AudioTimelineEntry, ...] = ()


@dataclass(frozen=True, slots=True)
class DebateResult:
    topic: str
    background: str
    research: ResearchBrief
    transcript: tuple[DebateTurn, ...]
    debate_package: Mapping[str, Any]
    provider: str
    model: str
    audio: AudioArtifact | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "debate_package", MappingProxyType(dict(self.debate_package)))

    # These aliases keep the original graph-oriented case-study API usable for
    # callers that only need to know whether the directed discussion finished.
    @property
    def completed(self) -> bool:
        return True

    @property
    def history(self) -> tuple[str, ...]:
        return ("opening", "optimist", "skeptic", "synthesis")

    @property
    def data(self) -> Mapping[str, str]:
        closing = next(
            (turn.text for turn in reversed(self.transcript) if turn.speaker == "Marcus"), ""
        )
        return MappingProxyType({"synthesis": closing})


@dataclass(frozen=True, slots=True)
class TurnInstruction:
    speaker: str
    phase: str
    task: str


LIVE_SCHEDULE = (
    TurnInstruction("Marcus", "OPENING", "Introduce the question and the trade-off neutrally."),
    TurnInstruction("Alex", "BUILD", "Make the strongest practical case for adoption."),
    TurnInstruction("Sarah", "BUILD", "Make the strongest safety-first case against adoption."),
    TurnInstruction(
        "Marcus", "CLASH", "Ask each side to address the other side's strongest point."
    ),
    TurnInstruction(
        "Alex", "CLASH", "Respond directly to the safety concern and concede one limit."
    ),
    TurnInstruction(
        "Sarah", "CLASH", "Respond directly to the access concern and concede one limit."
    ),
    TurnInstruction(
        "Marcus",
        "CLOSING",
        "Summarize agreement, disagreement, and one evidence-based next step. Do not pick a winner.",
    ),
)

SPEAKER_VOICES = {
    "Marcus": "am_adam",
    "Alex": "bm_george",
    "Sarah": "af_bella",
}


def _read_object(path: Path, label: str) -> Mapping[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Missing {label} fixture: {path.name}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {label} fixture: {path.name}") from exc
    if not isinstance(payload, Mapping):
        raise ValueError(f"{label} fixture must contain a JSON object")
    return payload


def _required_text(payload: Mapping[str, Any], key: str, label: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} needs a non-empty {key!r}")
    return value.strip()


def _load_research() -> ResearchBrief:
    payload = _read_object(RESEARCH_PATH, "research")
    signal = payload.get("signal")
    facts_payload = payload.get("facts")
    debate = payload.get("debate")
    if not all(isinstance(value, Mapping) for value in (signal, facts_payload, debate)):
        raise ValueError("Research fixture needs signal, facts, and debate objects")
    facts = facts_payload.get("facts")
    if (
        not isinstance(facts, list)
        or not facts
        or not all(isinstance(fact, str) and fact.strip() for fact in facts)
    ):
        raise ValueError("Research fixture needs a non-empty facts list")
    title = _required_text(signal, "title", "research signal")
    if title != "Disk Polishing Goes Open Source - Hackaday":
        raise ValueError("Replay research fixture is not the selected Hackaday record")
    return ResearchBrief(
        title=title,
        source=_required_text(signal, "source", "research signal"),
        published_at=_required_text(signal, "publishedAt", "research signal"),
        facts=tuple(fact.strip() for fact in facts),
        topic=_required_text(debate, "topic", "research debate"),
        background=_required_text(debate, "background", "research debate"),
    )


def _validate_transcript(payload: object) -> tuple[DebateTurn, ...]:
    if not isinstance(payload, list) or not payload:
        raise ValueError("Episode fixture needs a non-empty transcript list")
    turns: list[DebateTurn] = []
    phase_indexes: list[int] = []
    for index, raw_turn in enumerate(payload, start=1):
        if not isinstance(raw_turn, Mapping):
            raise ValueError(f"Transcript turn {index} must be an object")
        speaker = _required_text(raw_turn, "speaker", f"transcript turn {index}")
        phase = _required_text(raw_turn, "phase", f"transcript turn {index}")
        if speaker not in REPLAY_SPEAKERS:
            raise ValueError(f"Transcript turn {index} has an unsupported speaker: {speaker}")
        if phase not in PHASE_ORDER:
            raise ValueError(f"Transcript turn {index} has an unsupported phase: {phase}")
        turns.append(
            DebateTurn(speaker, _required_text(raw_turn, "text", f"transcript turn {index}"), phase)
        )
        phase_indexes.append(PHASE_ORDER.index(phase))
    if phase_indexes != sorted(phase_indexes):
        raise ValueError("Transcript phases must progress without going backwards")
    if turns[0].speaker != "Marcus" or turns[0].phase != "OPENING":
        raise ValueError("Transcript must begin with the moderator opening")
    if turns[-1].speaker != "Marcus" or turns[-1].phase != "CLOSING":
        raise ValueError("Transcript must end with the moderator closing")
    return tuple(turns)


def replay() -> DebateResult:
    """Load the supplied research record, first saved episode, and its MP3 offline."""
    research = _load_research()
    episode = _read_object(EPISODE_PATH, "episode")
    topic = _required_text(episode, "topic", "episode")
    if topic != research.topic:
        raise ValueError("Episode topic does not match the selected research record")
    duration = episode.get("duration")
    if not isinstance(duration, (int, float)) or duration <= 0:
        raise ValueError("Episode needs a positive numeric duration")
    audio_url = _required_text(episode, "audioUrl", "episode")
    if Path(audio_url).name != AUDIO_PATH.name or not AUDIO_PATH.is_file():
        raise ValueError("The replay audio file is missing or does not match the episode")
    debate_package = episode.get("debatePackage")
    if not isinstance(debate_package, Mapping):
        raise ValueError("Episode needs a debatePackage object")
    return DebateResult(
        topic=topic,
        background=_required_text(episode, "summary", "episode"),
        research=research,
        transcript=_validate_transcript(episode.get("transcript")),
        debate_package=debate_package,
        provider="replay",
        model="stored-episode",
        audio=AudioArtifact(AUDIO_PATH, float(duration)),
    )


def _live_prompt(
    research: ResearchBrief, instruction: TurnInstruction, transcript: Sequence[DebateTurn]
) -> str:
    history = "\n".join(f"{turn.speaker}: {turn.text}" for turn in transcript[-4:]) or "(none)"
    facts = "\n".join(f"- {fact}" for fact in research.facts)
    return f"""You are {instruction.speaker} in a short technical podcast debate.
Topic: {research.topic}
Reviewed source facts (use only these as factual claims):
{facts}

Phase: {instruction.phase}
Your task: {instruction.task}
Recent transcript:
{history}

Speak in 55 words or fewer. Clearly label uncertain claims as questions or opinions.
Do not invent test results, standards, product capabilities, statistics, or sources."""


def generate_live_debate(
    provider: LLMProvider, model: str, research: ResearchBrief
) -> DebateResult:
    """Generate a seven-turn, fact-bounded debate; audio is deliberately not generated."""
    transcript: list[DebateTurn] = []
    for instruction in LIVE_SCHEDULE:
        response = provider.generate(
            LLMRequest(
                model,
                (Message("user", _live_prompt(research, instruction, transcript)),),
                max_output_tokens=160,
                temperature=0.35,
            )
        )
        text = response.text.strip()
        if not text:
            raise ValueError(f"{instruction.speaker} returned an empty debate turn")
        transcript.append(DebateTurn(instruction.speaker, text, instruction.phase))
    return DebateResult(
        topic=research.topic,
        background=research.background,
        research=research,
        transcript=tuple(transcript),
        debate_package={},
        provider=provider.name,
        model=model,
    )


def synthesize_episode_audio(
    result: DebateResult,
    *,
    output_path: Path,
    synthesizer: SpeechSynthesizer,
    overwrite: bool = False,
    duration_reader: Callable[[bytes], float] | None = None,
) -> DebateResult:
    """Render every ordered debate line with its mapped voice and save one MP3.

    The caller supplies a concrete synthesizer so tests can use a local fake
    and the case study never turns a replay into a network call accidentally.
    """
    render_options: dict[str, Any] = {}
    if duration_reader is not None:
        render_options["duration_reader"] = duration_reader
    rendered = render_mp3_segments(
        tuple(SpeechSegment(turn.speaker, turn.text) for turn in result.transcript),
        voices=SPEAKER_VOICES,
        synthesizer=synthesizer,
        **render_options,
    )
    path = write_mp3(output_path, rendered, overwrite=overwrite)
    return replace(
        result,
        audio=AudioArtifact(path, rendered.duration_seconds, rendered.timeline),
    )


def run(*, allow_live: bool = False) -> DebateResult:
    """Run the live director only with explicit authorization; mock mode returns the replay."""
    factory = ProviderFactory()
    if factory.kind == "mock":
        return replay()
    if not allow_live:
        raise ConfigurationError("Live model detected: pass --live, or use --replay instead.")
    selected = factory.create(allow_live=True)
    provider = selected.provider
    try:
        return generate_live_debate(provider, selected.model, _load_research())
    finally:
        close = getattr(provider, "close", None)
        if callable(close):
            close()


def _result_as_dict(result: DebateResult) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "topic": result.topic,
        "background": result.background,
        "research": asdict(result.research),
        "transcript": [asdict(turn) for turn in result.transcript],
        "debatePackage": dict(result.debate_package),
        "provider": result.provider,
        "model": result.model,
        "audio": None,
    }
    if result.audio:
        payload["audio"] = {
            "path": str(result.audio.path),
            "durationSeconds": result.audio.duration_seconds,
            "timeline": [
                {
                    "speaker": entry.speaker,
                    "start": entry.start_seconds,
                    "end": entry.end_seconds,
                    "duration": entry.duration_seconds,
                }
                for entry in result.audio.timeline
            ],
        }
    return payload


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Run or replay a compact, grounded podcast debate."
    )
    parser.add_argument("--live", action="store_true", help="Authorize seven live LLM calls.")
    parser.add_argument(
        "--replay", action="store_true", help="Load the saved episode and local MP3."
    )
    parser.add_argument(
        "--synthesize-audio",
        action="store_true",
        help="Authorize tts.ai calls to render the chosen replay or live transcript.",
    )
    parser.add_argument(
        "--audio-output",
        type=Path,
        default=Path("artifacts/autonomous_debate/rendered-debate.mp3"),
        help="MP3 destination for --synthesize-audio (refuses to overwrite by default).",
    )
    parser.add_argument(
        "--overwrite-audio",
        action="store_true",
        help="Allow --synthesize-audio to replace an existing --audio-output file.",
    )
    args = parser.parse_args(argv)

    if args.synthesize_audio:
        if args.replay:
            parser.error("--replay already includes captured audio; do not use --synthesize-audio.")
        if args.live:
            factory = ProviderFactory()
            if factory.kind == "mock":
                parser.error(
                    "--live needs a configured LLM provider; use --replay to render saved audio."
                )
            result = run(allow_live=True)
        else:
            parser.error("--synthesize-audio requires --live.")
        factory = ProviderFactory()
        try:
            with TtsAiProvider(
                api_key=factory.env.get("TTS_AI_KEY"), timeout_seconds=factory.timeout
            ) as synthesizer:
                result = synthesize_episode_audio(
                    result,
                    output_path=args.audio_output,
                    synthesizer=synthesizer,
                    overwrite=args.overwrite_audio,
                )
        except (ConfigurationError, FileExistsError, ValueError) as exc:
            parser.error(str(exc))
        print(json.dumps(_result_as_dict(result), indent=2, ensure_ascii=True))
        return
    if args.replay:
        print(json.dumps(_result_as_dict(replay()), indent=2, ensure_ascii=True))
        return
    factory = ProviderFactory()
    if factory.kind == "mock":
        print("No live LLM model is configured. Run with --replay to inspect the saved episode.")
        return
    if not args.live:
        print("A live LLM model is configured. Run with --live, or use --replay instead.")
        return
    print(json.dumps(_result_as_dict(run(allow_live=True)), indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
