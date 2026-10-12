"""Process-local token-bucket request limiting and concurrency limits."""

from __future__ import annotations

import math
import threading
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager

from applied_ai.core.exceptions import (
    ConcurrencyLimitError,
    RequestDeadlineExceededError,
)


class TokenBucketLimiter:
    """Thread-safe local limiter; distributed deployments require a shared store."""

    def __init__(
        self,
        requests_per_second: float,
        *,
        burst: int = 1,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if not math.isfinite(requests_per_second) or requests_per_second <= 0:
            raise ValueError("requests_per_second must be positive and finite")
        if type(burst) is not int or burst < 1:
            raise ValueError("burst must be >= 1")
        self._rate = requests_per_second
        self._capacity = burst
        self._tokens = float(burst)
        self._last = clock()
        self._clock = clock
        self._sleep = sleep
        self._lock = threading.Lock()

    def acquire(self, *, deadline: float | None = None) -> None:
        while True:
            with self._lock:
                now = self._clock()
                self._tokens = min(
                    self._capacity, self._tokens + max(0.0, now - self._last) * self._rate
                )
                self._last = now
                if deadline is not None and now >= deadline:
                    raise RequestDeadlineExceededError("Rate limit waiting exceeded deadline")
                if self._tokens >= 1:
                    self._tokens -= 1
                    return
                wait = (1 - self._tokens) / self._rate
                if deadline is not None and wait >= deadline - now:
                    raise RequestDeadlineExceededError("Not enough time to wait for rate limit")
            self._sleep(wait)


class ConcurrencyLimiter:
    """Limit simultaneous calls in one process, with bounded lock acquisition."""

    def __init__(self, max_concurrent: int) -> None:
        if type(max_concurrent) is not int or max_concurrent < 1:
            raise ValueError("max_concurrent must be >= 1")
        self._semaphore = threading.BoundedSemaphore(max_concurrent)

    @contextmanager
    def slot(self, *, timeout_seconds: float) -> Iterator[None]:
        if not self._semaphore.acquire(timeout=max(0.0, timeout_seconds)):
            raise ConcurrencyLimitError("Concurrent request limit reached")
        try:
            yield
        finally:
            self._semaphore.release()
