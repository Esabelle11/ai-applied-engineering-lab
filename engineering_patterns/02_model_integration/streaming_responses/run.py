"""A small, provider-neutral streaming protocol with an offline implementation."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class StreamChunk:
    index: int
    text: str
    final: bool = False

    def __post_init__(self) -> None:
        if self.index < 0:
            raise ValueError("Chunk index must be non-negative")


class TextStreamingProvider(Protocol):
    def stream(self, prompt: str) -> Iterator[StreamChunk]: ...


class MockStreamingProvider:
    """Offline stream source that preserves chunk order and marks the terminal chunk."""

    def __init__(self, response: str, *, chunk_size: int = 4) -> None:
        if not response or chunk_size < 1:
            raise ValueError("response must be non-empty and chunk_size must be positive")
        self.response = response
        self.chunk_size = chunk_size

    def stream(self, prompt: str) -> Iterator[StreamChunk]:
        if not prompt.strip():
            raise ValueError("prompt must be non-empty")
        fragments = [self.response[index : index + self.chunk_size] for index in range(0, len(self.response), self.chunk_size)]
        for index, fragment in enumerate(fragments):
            yield StreamChunk(index, fragment, final=index == len(fragments) - 1)


def collect_stream(chunks: Iterator[StreamChunk]) -> str:
    """Reject out-of-order or unterminated streams instead of silently returning partial output."""
    parts: list[str] = []
    final_seen = False
    for expected, chunk in enumerate(chunks):
        if final_seen or chunk.index != expected:
            raise ValueError("Stream chunks must be ordered and terminal only once")
        parts.append(chunk.text)
        print(f"Received chunk {chunk.index}: {chunk.text!r} (final={chunk.final})")
        final_seen = chunk.final
    if not final_seen:
        raise ValueError("Stream ended without a terminal chunk")
    return "".join(parts)


def main() -> None:
    print(collect_stream(MockStreamingProvider("streamed response", chunk_size=5).stream("Say hello")))


if __name__ == "__main__":
    main()
