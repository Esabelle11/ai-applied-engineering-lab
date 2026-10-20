"""Explicit, deterministic optimization helpers for handbook examples."""

from __future__ import annotations

import asyncio
import re
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass

from applied_ai.knowledge import cosine_similarity, embed_text


def batch_items[T](items: Sequence[T], *, size: int) -> tuple[tuple[T, ...], ...]:
    if size < 1:
        raise ValueError("size must be positive")
    return tuple(tuple(items[index : index + size]) for index in range(0, len(items), size))


async def bounded_map[T, R](
    items: Sequence[T], operation: Callable[[T], Awaitable[R]], *, max_concurrency: int
) -> list[R]:
    if max_concurrency < 1:
        raise ValueError("max_concurrency must be positive")
    gate = asyncio.Semaphore(max_concurrency)

    async def one(item: T) -> R:
        async with gate:
            return await operation(item)

    return list(await asyncio.gather(*(one(item) for item in items)))


def compress_text(text: str, *, max_words: int) -> str:
    if not text.strip() or max_words < 1:
        raise ValueError("text and max_words are required")
    return " ".join(text.split()[:max_words])


def estimate_tokens(text: str) -> int:
    if not text.strip():
        return 0
    return len(re.findall(r"\w+|[^\w\s]", text))


class SemanticCache:
    def __init__(self, *, threshold: float = 0.9) -> None:
        if not 0 <= threshold <= 1:
            raise ValueError("threshold must be in [0, 1]")
        self.threshold = threshold
        self._entries: list[tuple[str, str, tuple[float, ...]]] = []

    def put(self, query: str, response: str) -> None:
        if not query.strip() or not response.strip():
            raise ValueError("query and response are required")
        self._entries.append((query, response, embed_text(query)))

    def get(self, query: str) -> str | None:
        vector = embed_text(query)
        for _, response, candidate in self._entries:
            if cosine_similarity(vector, candidate) >= self.threshold:
                return response
        return None


@dataclass(frozen=True, slots=True)
class ModelOption:
    name: str
    latency_ms: float
    cost_per_request: float
    quality: float

    def __post_init__(self) -> None:
        if (
            not self.name.strip()
            or min(self.latency_ms, self.cost_per_request) < 0
            or not 0 <= self.quality <= 1
        ):
            raise ValueError("Invalid model option")


def cheapest_qualified(options: Sequence[ModelOption], *, minimum_quality: float) -> ModelOption:
    eligible = [option for option in options if option.quality >= minimum_quality]
    if not eligible:
        raise ValueError("No model meets minimum quality")
    return min(
        eligible, key=lambda option: (option.cost_per_request, option.latency_ms, option.name)
    )


def fastest_qualified(options: Sequence[ModelOption], *, minimum_quality: float) -> ModelOption:
    eligible = [option for option in options if option.quality >= minimum_quality]
    if not eligible:
        raise ValueError("No model meets minimum quality")
    return min(
        eligible, key=lambda option: (option.latency_ms, option.cost_per_request, option.name)
    )


def pareto_frontier(options: Sequence[ModelOption]) -> tuple[ModelOption, ...]:
    return tuple(
        option
        for option in options
        if not any(
            other is not option
            and other.quality >= option.quality
            and other.cost_per_request <= option.cost_per_request
            and (other.quality > option.quality or other.cost_per_request < option.cost_per_request)
            for other in options
        )
    )
