"""Offline coverage for WhyBuddy replay and the complete live-media flow."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from applied_ai.providers.mock import MockProvider
from case_studies.whybuddy.run import Lesson, compose_video, generate_lesson, render_images, replay


def test_replay_uses_the_supplied_bee_lesson_and_completed_video() -> None:
    result = replay()

    assert result.question == "Why do bees make honey?"
    assert result.video.name == "final_eebf368b7c694705b673059aa602c7a3.mp4"
    assert result.video.is_file()
    assert result.audio.is_file()
    assert len(result.images) == 7
    assert all(path.is_file() for path in result.images)


def test_live_llm_lesson_is_structured_before_media_generation() -> None:
    provider = MockProvider(
        default_text=json.dumps(
            {
                "script": "Leaves change color when trees prepare for colder weather.",
                "imagePrompts": ["one", "two", "three"],
            }
        )
    )

    lesson = generate_lesson(provider, "test-model", "Why do leaves change color?")

    assert provider.call_count == 1
    assert lesson.question == "Why do leaves change color?"
    assert len(lesson.image_prompts) == 3


def test_images_and_audio_are_combined_into_mp4(tmp_path: Path, monkeypatch) -> None:
    class FakeImage:
        def save(self, path: Path) -> None:
            path.write_bytes(b"fake-png")

    class FakePipeline:
        def __call__(self, _prompt: str, **_kwargs: object) -> object:
            return type("ImageResult", (), {"images": [FakeImage()]})()

    lesson = Lesson("Why?", "A short answer.", ("one", "two", "three"), "mock", "test")
    images = render_images(lesson, tmp_path, pipeline=FakePipeline())
    audio = tmp_path / "narration.mp3"
    audio.write_bytes(b"fake-mp3")
    video = tmp_path / "lesson.mp4"

    def fake_run(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        assert "concat=n=3:v=1:a=0" in command[command.index("-filter_complex") + 1]
        assert command[-1] == str(video)
        video.write_bytes(b"fake-mp4")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    assert compose_video(images, audio, video, audio_duration_seconds=12.0) == video
    assert video.read_bytes() == b"fake-mp4"
