"""Normalized provider response with optional usage and measured wall-clock latency."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class TokenUsage:
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None

    def __post_init__(self) -> None:
        for field in (self.input_tokens, self.output_tokens, self.total_tokens):
            if field is not None and (type(field) is not int or field < 0):
                raise ValueError("Token counts must be non-negative integers or None")


@dataclass(frozen=True, slots=True)
class ReliabilityStats:
    """Local orchestration telemetry, with no prompt or sensitive response content."""

    attempts: int
    failovers: int
    elapsed_seconds: float
    error_categories: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class LLMResponse:
    text: str
    model: str
    provider: str
    request_id: str | None = None
    finish_reason: str | None = None
    usage: TokenUsage | None = None
    latency_seconds: float | None = None
    parsed_output: dict[str, Any] | None = None
    reliability: ReliabilityStats | None = None
