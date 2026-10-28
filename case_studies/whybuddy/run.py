from __future__ import annotations

import argparse
import json
import subprocess
import uuid
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from applied_ai.core import (
    ConfigurationError,
    LLMProvider,
    LLMRequest,
    Message,
    StructuredOutputSpec,
)
from applied_ai.core.structured import parse_structured_output
from applied_ai.media import (
    RenderedMP3,
    SpeechSegment,
    TtsAiProvider,
    render_mp3_segments,
    write_mp3,
)
from applied_ai.providers.factory import ProviderFactory

DEFAULT_QUESTION = "Why do bees make honey?"
DATA_DIR = Path(__file__).resolve().parent / "data"
REPLAY_PATH = DATA_DIR / "bee_honey_replay.json"
REPLAY_DIR = DATA_DIR / "bee_honey_replay"
ARTIFACTS_DIR = Path("artifacts") / "whybuddy"
IMAGE_MODEL = "Lykon/dreamshaper-7"

LESSON_SYSTEM = """You are WhyBuddy, a patient science teacher for children.
Answer the student's question in simple, accurate, friendly language. Return a
short narration and 3 to 7 child-safe cartoon scene prompts. Each image prompt
must describe a visual scene and say that it contains no written words."""

LESSON_SCHEMA = {
    "type": "object",
    "properties": {
        "script": {"type": "string", "minLength": 1, "maxLength": 1_200},
        "imagePrompts": {
            "type": "array",
            "minItems": 3,
            "maxItems": 7,
            "items": {"type": "string", "minLength": 1},
        },
    },
    "required": ["script", "imagePrompts"],
    "additionalProperties": False,
}


@dataclass(frozen=True, slots=True)
class Lesson:
    question: str
    script: str
    image_prompts: tuple[str, ...]
    provider: str
    model: str


@dataclass(frozen=True, slots=True)
class LessonOutput:
    """Every file needed to replay or share a finished WhyBuddy lesson."""

    question: str
    script: str
    provider: str
    model: str
    output_dir: Path
    images: tuple[Path, ...]
    audio: Path
    video: Path
    audio_duration_seconds: float | None = None


def _lesson_from_payload(
    question: str, payload: Mapping[str, Any], *, provider: str, model: str
) -> Lesson:
    parsed = parse_structured_output(
        json.dumps(dict(payload)),
        StructuredOutputSpec("whybuddy_lesson", LESSON_SCHEMA),
        provider=provider,
    )
    return Lesson(
        question=question,
        script=parsed["script"],
        image_prompts=tuple(parsed["imagePrompts"]),
        provider=provider,
        model=model,
    )


def replay() -> LessonOutput:
    """Use the supplied bee lesson and completed audio-video assets; no API calls."""
    capture = json.loads(REPLAY_PATH.read_text(encoding="utf-8"))
    if not isinstance(capture, dict):
        raise ValueError("WhyBuddy replay fixture must be a JSON object")
    question = capture.get("question")
    script = capture.get("script")
    prompts = capture.get("imagePrompts")
    video_name = capture.get("video")
    audio_name = capture.get("audio")
    if (
        not isinstance(question, str)
        or not isinstance(script, str)
        or not isinstance(prompts, list)
    ):
        raise ValueError("WhyBuddy replay fixture is missing lesson content")
    if not isinstance(video_name, str) or not isinstance(audio_name, str):
        raise ValueError("WhyBuddy replay fixture is missing media paths")
    video = DATA_DIR / video_name
    audio = DATA_DIR / audio_name
    images = tuple(REPLAY_DIR / f"slide_{index}.png" for index in range(len(prompts)))
    if not video.is_file() or not audio.is_file() or not all(path.is_file() for path in images):
        raise ValueError("WhyBuddy replay media is incomplete")
    return LessonOutput(
        question=question,
        script=script,
        provider="replay",
        model="captured-whybuddy",
        output_dir=REPLAY_DIR,
        images=images,
        audio=audio,
        video=video,
        audio_duration_seconds=24.576,
    )


def generate_lesson(provider: LLMProvider, model: str, question: str) -> Lesson:
    """Ask the configured live LLM for narration and image prompts in one call."""
    if not question.strip():
        raise ValueError("Question must not be empty")
    output_spec = StructuredOutputSpec("whybuddy_lesson", LESSON_SCHEMA)
    response = provider.generate(
        LLMRequest(
            model,
            (
                Message("system", LESSON_SYSTEM),
                Message("user", f"Student question:\n\n{question.strip()}"),
            ),
            max_output_tokens=1_000,
            temperature=0.4,
            response_format=output_spec if provider.capabilities.structured_output else None,
        )
    )
    payload = (
        response.parsed_output
        if response.parsed_output is not None
        else parse_structured_output(response.text, output_spec, provider=provider.name)
    )
    if not isinstance(payload, Mapping):
        raise ValueError("WhyBuddy provider returned a non-object lesson")
    return _lesson_from_payload(
        question.strip(), payload, provider=response.provider, model=response.model
    )


def _load_image_pipeline() -> Any:
    """Load DreamShaper once, only for a live lesson."""
    try:
        import torch
        from diffusers import StableDiffusionPipeline
    except ImportError as exc:
        raise ConfigurationError(
            "Live images need: uv sync --extra media --extra providers"
        ) from exc
    device = (
        "cuda"
        if torch.cuda.is_available()
        else "mps"
        if torch.backends.mps.is_available()
        else "cpu"
    )
    dtype = torch.float16 if device in {"cuda", "mps"} else torch.float32
    try:
        pipeline = StableDiffusionPipeline.from_pretrained(
            IMAGE_MODEL, torch_dtype=dtype, use_safetensors=True
        )
        pipeline.to(device)
        return pipeline
    except Exception as exc:
        raise ConfigurationError(
            "Could not load DreamShaper. Check Hugging Face access, memory, and network connection."
        ) from exc


def render_images(lesson: Lesson, output_dir: Path, *, pipeline: Any) -> tuple[Path, ...]:
    """Save one PNG for each structured image prompt."""
    paths: list[Path] = []
    for index, prompt in enumerate(lesson.image_prompts):
        image_path = output_dir / f"slide_{index}.png"
        result = pipeline(prompt, num_inference_steps=20, guidance_scale=7.5)
        images = getattr(result, "images", None)
        if not isinstance(images, list) or not images:
            raise ValueError(f"Image generator returned no image for scene {index}")
        images[0].save(image_path)
        paths.append(image_path)
    return tuple(paths)


def synthesize_audio(
    lesson: Lesson, output_dir: Path, *, api_key: str | None, timeout: float
) -> tuple[Path, RenderedMP3]:
    """Use the SDK's tts.ai adapter and save one MP3 narration."""
    with TtsAiProvider(api_key=api_key, timeout_seconds=timeout) as synthesizer:
        rendered = render_mp3_segments(
            (SpeechSegment("WhyBuddy", lesson.script),),
            voices={"WhyBuddy": "af_bella"},
            synthesizer=synthesizer,
        )
    audio_path = write_mp3(output_dir / "narration.mp3", rendered)
    return audio_path, rendered


def compose_video(
    images: Sequence[Path], audio: Path, output: Path, *, audio_duration_seconds: float
) -> Path:
    """Combine the slide PNGs and narration MP3 into one H.264/AAC MP4 with ffmpeg."""
    if not images:
        raise ValueError("At least one image is required to compose a WhyBuddy video")
    if audio_duration_seconds <= 0:
        raise ValueError("Narration must have a positive duration")
    seconds_per_image = max(4.0, audio_duration_seconds / len(images))
    command = ["ffmpeg", "-y"]
    for image in images:
        command.extend(["-loop", "1", "-t", f"{seconds_per_image:.3f}", "-i", str(image)])
    command.extend(["-i", str(audio)])
    image_inputs = "".join(f"[{index}:v]" for index in range(len(images)))
    command.extend(
        [
            "-filter_complex",
            f"{image_inputs}concat=n={len(images)}:v=1:a=0,fps=24,format=yuv420p[video]",
            "-map",
            "[video]",
            "-map",
            f"{len(images)}:a",
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-shortest",
            str(output),
        ]
    )
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=600)
    except FileNotFoundError as exc:
        raise ConfigurationError("ffmpeg is required to create the WhyBuddy MP4") from exc
    except subprocess.TimeoutExpired as exc:
        raise ConfigurationError("ffmpeg timed out while creating the WhyBuddy MP4") from exc
    if result.returncode != 0 or not output.is_file():
        raise RuntimeError(f"ffmpeg could not create the WhyBuddy MP4: {result.stderr[-500:]}")
    return output


def _write_lesson(lesson: Lesson, output_dir: Path) -> Path:
    path = output_dir / "lesson.json"
    path.write_text(
        json.dumps(
            {
                "question": lesson.question,
                "script": lesson.script,
                "imagePrompts": list(lesson.image_prompts),
                "provider": lesson.provider,
                "model": lesson.model,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def run(
    *, question: str = DEFAULT_QUESTION, allow_live: bool = False, output_dir: Path | None = None
) -> LessonOutput:
    """Run the entire live pipeline and save the lesson, PNGs, MP3, and final MP4."""
    factory = ProviderFactory()
    if factory.kind == "mock":
        raise ConfigurationError(
            "No live LLM is configured. Use --replay or configure a provider in .env."
        )
    if not allow_live:
        raise ConfigurationError("Live generation needs --live.")
    target_dir = output_dir or ARTIFACTS_DIR / uuid.uuid4().hex
    if target_dir.exists():
        raise FileExistsError(f"WhyBuddy output directory already exists: {target_dir}")
    target_dir.mkdir(parents=True)
    selected = factory.create(allow_live=True)
    provider = selected.provider
    try:
        lesson = generate_lesson(provider, selected.model, question)
    finally:
        close = getattr(provider, "close", None)
        if callable(close):
            close()
    _write_lesson(lesson, target_dir)
    images = render_images(lesson, target_dir, pipeline=_load_image_pipeline())
    audio, rendered = synthesize_audio(
        lesson, target_dir, api_key=factory.env.get("TTS_AI_KEY"), timeout=factory.timeout
    )
    video = compose_video(
        images, audio, target_dir / "lesson.mp4", audio_duration_seconds=rendered.duration_seconds
    )
    return LessonOutput(
        question=lesson.question,
        script=lesson.script,
        provider=lesson.provider,
        model=lesson.model,
        output_dir=target_dir,
        images=images,
        audio=audio,
        video=video,
        audio_duration_seconds=rendered.duration_seconds,
    )


def _as_dict(result: LessonOutput) -> dict[str, Any]:
    return {
        "question": result.question,
        "script": result.script,
        "provider": result.provider,
        "model": result.model,
        "outputDir": str(result.output_dir),
        "images": [str(path) for path in result.images],
        "audio": str(result.audio),
        "audioDurationSeconds": result.audio_duration_seconds,
        "video": str(result.video),
    }


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Create or replay a complete WhyBuddy lesson video."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--live", action="store_true", help="Run LLM, image, TTS, and MP4 generation."
    )
    mode.add_argument(
        "--replay", action="store_true", help="Show the supplied bee lesson and finished MP4."
    )
    parser.add_argument("--question", default=DEFAULT_QUESTION, help="Student question for --live.")
    parser.add_argument("--output-dir", type=Path, help="New directory for a complete live lesson.")
    args = parser.parse_args(argv)

    if args.replay:
        print(json.dumps(_as_dict(replay()), indent=2, ensure_ascii=False))
        return
    if not args.live:
        parser.print_help()
        return
    try:
        print(
            json.dumps(
                _as_dict(run(question=args.question, allow_live=True, output_dir=args.output_dir)),
                indent=2,
                ensure_ascii=False,
            )
        )
    except (ConfigurationError, FileExistsError, RuntimeError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
