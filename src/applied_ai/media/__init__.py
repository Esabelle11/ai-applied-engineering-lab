"""Explicit media-provider interfaces and local audio assembly helpers."""

from applied_ai.media.tts import (
    AudioTimelineEntry,
    RenderedMP3,
    SpeechSegment,
    SpeechSynthesizer,
    TtsAiProvider,
    render_mp3_segments,
    write_mp3,
)

__all__ = [
    "AudioTimelineEntry",
    "RenderedMP3",
    "SpeechSegment",
    "SpeechSynthesizer",
    "TtsAiProvider",
    "render_mp3_segments",
    "write_mp3",
]
