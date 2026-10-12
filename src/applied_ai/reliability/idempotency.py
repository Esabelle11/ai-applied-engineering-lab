"""Single-process deduplication helper for side-effecting tool examples."""

from __future__ import annotations

import threading
from collections.abc import Callable
from typing import TypeVar, cast

T = TypeVar("T")


class IdempotencyGuard:
    """Cache *successful* operations by caller-provided key (not durable/distributed)."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._cache: dict[str, object] = {}

    def run_once(self, key: str, action: Callable[[], T]) -> T:
        if not key.strip():
            raise ValueError("Idempotency key must not be empty")
        with self._lock:
            if key not in self._cache:
                self._cache[key] = action()
            return cast(T, self._cache[key])
