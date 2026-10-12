"""Bounded exponential backoff; Retry-After is a minimum waiting period."""

from __future__ import annotations

import math
from dataclasses import dataclass

from applied_ai.core.exceptions import LLMError


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    max_attempts: int = 3
    initial_delay_seconds: float = 0.25
    max_delay_seconds: float = 5.0
    multiplier: float = 2.0
    jitter: bool = True

    def __post_init__(self) -> None:
        if type(self.max_attempts) is not int or self.max_attempts < 1:
            raise ValueError("max_attempts must be a positive integer")
        if not all(
            math.isfinite(v) and v >= 0
            for v in (self.initial_delay_seconds, self.max_delay_seconds)
        ):
            raise ValueError("delay bounds must be finite and nonnegative")
        if not math.isfinite(self.multiplier) or self.multiplier < 1:
            raise ValueError("multiplier must be finite and >= 1")

    def delay_seconds(self, attempt: int, error: LLMError, random_fraction: float) -> float:
        """Compute delay *after* 1-indexed attempt, before the next attempt."""
        if attempt < 1 or not 0 <= random_fraction <= 1:
            raise ValueError("Invalid attempt or random fraction")
        # Avoid float overflow with a bounded exponent.
        if self.initial_delay_seconds == 0:
            scaled = 0.0
        else:
            try:
                scaled = self.initial_delay_seconds * self.multiplier ** min(attempt - 1, 64)
            except OverflowError:
                scaled = float("inf")
        base = min(self.max_delay_seconds, scaled)
        delay = base * random_fraction if self.jitter else base
        if error.retry_after_seconds is not None:
            delay = max(delay, error.retry_after_seconds)
        return delay
