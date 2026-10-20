"""Small reliability helpers for explicit, offline-safe workflow boundaries."""

from __future__ import annotations

import json
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeVar

from applied_ai.core.exceptions import LLMError

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class ErrorClassification:
    category: str
    retryable: bool


def classify_error(error: Exception) -> ErrorClassification:
    """Classify normalized LLM failures without inspecting secret-bearing payloads."""
    if isinstance(error, LLMError):
        return ErrorClassification(error.category, error.retryable)
    if isinstance(error, TimeoutError):
        return ErrorClassification("timeout", True)
    if isinstance(error, ConnectionError):
        return ErrorClassification("connection", True)
    return ErrorClassification("unknown", False)


def full_jitter(max_delay_seconds: float, fraction: float) -> float:
    if max_delay_seconds < 0 or not 0 <= fraction <= 1:
        raise ValueError("delay and random fraction must be within bounds")
    return max_delay_seconds * fraction


class RequestQueue:
    """Bounded in-memory FIFO queue; callers decide when and how to drain it."""

    def __init__(self, *, max_size: int = 100) -> None:
        if max_size < 1:
            raise ValueError("max_size must be positive")
        self._max_size = max_size
        self._items: deque[T] = deque()

    def enqueue(self, item: T) -> None:
        if len(self._items) >= self._max_size:
            raise OverflowError("Request queue is full")
        self._items.append(item)

    def drain(self, handler: Callable[[T], Any]) -> list[Any]:
        results: list[Any] = []
        while self._items:
            results.append(handler(self._items.popleft()))
        return results

    @property
    def size(self) -> int:
        return len(self._items)


def validate_text_output(value: object, *, allowed: set[str] | None = None) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Output must be non-empty text")
    normalized = value.strip()
    if allowed is not None and normalized not in allowed:
        raise ValueError("Output is outside the allowed set")
    return normalized


def recover_json_output(value: str, *, required_keys: set[str]) -> dict[str, Any]:
    """Decode and minimally validate JSON; never repair or execute arbitrary content."""
    try:
        decoded = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError("Output is not valid JSON") from exc
    if not isinstance(decoded, dict) or not required_keys.issubset(decoded):
        raise ValueError("Output is missing required JSON keys")
    return decoded


def with_degradation[T](
    primary: Callable[[], T], fallback: Callable[[], T], *, recoverable: tuple[type[Exception], ...]
) -> T:
    """Use a deliberately supplied fallback only for explicitly recoverable failures."""
    try:
        return primary()
    except recoverable:
        return fallback()
