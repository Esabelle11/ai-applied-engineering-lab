"""Thread-safe CLOSED / OPEN / HALF_OPEN circuit breaker for transient failures."""

from __future__ import annotations

import math
import threading
import time
from collections.abc import Callable
from enum import StrEnum

from applied_ai.core.exceptions import CircuitOpenError


class CircuitState(StrEnum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    def __init__(
        self,
        *,
        failure_threshold: int = 3,
        reset_timeout_seconds: float = 20.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if type(failure_threshold) is not int or failure_threshold < 1:
            raise ValueError("failure_threshold must be >= 1")
        if not math.isfinite(reset_timeout_seconds) or reset_timeout_seconds <= 0:
            raise ValueError("reset_timeout_seconds must be positive and finite")
        self._threshold = failure_threshold
        self._reset_timeout = reset_timeout_seconds
        self._clock = clock
        self._lock = threading.Lock()
        self._state = CircuitState.CLOSED
        self._failures = 0
        self._opened_at = 0.0
        self._probe_active = False

    @property
    def state(self) -> CircuitState:
        with self._lock:
            return self._state

    def before_call(self) -> None:
        with self._lock:
            if self._state == CircuitState.OPEN:
                if self._clock() - self._opened_at < self._reset_timeout:
                    raise CircuitOpenError("Provider circuit is open")
                self._state = CircuitState.HALF_OPEN
            if self._state == CircuitState.HALF_OPEN:
                if self._probe_active:
                    raise CircuitOpenError("Provider circuit probe is already in flight")
                self._probe_active = True

    def record_success(self) -> None:
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failures = 0
            self._probe_active = False

    def record_failure(self) -> None:
        with self._lock:
            self._failures += 1
            if self._state == CircuitState.HALF_OPEN or self._failures >= self._threshold:
                self._state = CircuitState.OPEN
                self._opened_at = self._clock()
            self._probe_active = False

    def abandon_call(self) -> None:
        """Release a half-open probe if local admission failed before a provider call."""
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._probe_active = False
