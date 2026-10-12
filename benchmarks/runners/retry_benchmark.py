"""Fair, fully simulated comparison of SDK RetryPolicy variants."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from applied_ai.core import LLMRequest, Message, TokenUsage
from applied_ai.core.exceptions import (
    AuthenticationError,
    LLMError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    RateLimitError,
)
from applied_ai.experimentation import ExperimentManifest, Observation
from applied_ai.providers.mock import MockProvider
from applied_ai.reliability import ReliableProvider, RetryPolicy


@dataclass
class VirtualClock:
    now: float = 0.0

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += seconds


class TimedMockProvider(MockProvider):
    def __init__(self, clock: VirtualClock, faults: list[LLMError]) -> None:
        super().__init__(
            default_text="ok",
            faults=faults,
            usage=TokenUsage(input_tokens=12, output_tokens=8, total_tokens=20),
        )
        self.clock = clock

    def generate(self, request: LLMRequest):  # type: ignore[no-untyped-def]
        self.clock.sleep(0.02)  # declared simulation: every attempt costs 20 ms
        return super().generate(request)


def make_error(source: dict[str, Any]) -> LLMError:
    kind = source["type"]
    kinds = {
        "rate_limit": RateLimitError,
        "unavailable": ProviderUnavailableError,
        "timeout": ProviderTimeoutError,
        "authentication": AuthenticationError,
    }
    if kind not in kinds:
        raise ValueError(f"Unknown injected error: {kind}")
    return kinds[kind](
        "Synthetic failure",
        retry_after_seconds=source.get("retry_after_seconds"),
    )


def run(spec: ExperimentManifest, dataset: Path) -> list[Observation]:
    cases = json.loads(dataset.read_text(encoding="utf-8"))
    strategies = {
        "no_retry": RetryPolicy(max_attempts=1, initial_delay_seconds=0, jitter=False),
        "fixed": RetryPolicy(
            max_attempts=3,
            initial_delay_seconds=0.1,
            max_delay_seconds=1,
            multiplier=1,
            jitter=False,
        ),
        "exponential": RetryPolicy(
            max_attempts=3,
            initial_delay_seconds=0.1,
            max_delay_seconds=1,
            multiplier=2,
            jitter=False,
        ),
        "exponential_jitter": RetryPolicy(
            max_attempts=3,
            initial_delay_seconds=0.1,
            max_delay_seconds=1,
            multiplier=2,
            jitter=True,
        ),
    }
    if set(spec.implementations) != set(strategies):
        raise ValueError("Retry strategy mismatch in manifest")
    records: list[Observation] = []
    for repeat in range(spec.repetitions):
        for case in cases:
            for name in spec.implementations:
                clock = VirtualClock()
                faults = [make_error(f) for f in case["faults"]]
                mock = TimedMockProvider(clock, faults)
                wrapped = ReliableProvider(
                    mock,
                    policy=strategies[name],
                    total_timeout_seconds=10,
                    clock=clock.monotonic,
                    sleep=clock.sleep,
                    random_fraction=lambda: 0.5,
                )
                try:
                    response = wrapped.generate(
                        LLMRequest("mock-model", (Message("user", "ping"),))
                    )
                except LLMError as exc:
                    records.append(
                        Observation(
                            spec.id,
                            case["id"],
                            name,
                            repeat,
                            "error",
                            not case["expected_success"],
                            round(clock.now, 6),
                            "simulated",
                            attempts=mock.call_count,
                            error_category=exc.category,
                            note="correct=True means matched expected success/failure, not answered",
                        )
                    )
                else:
                    usage = response.usage
                    records.append(
                        Observation(
                            spec.id,
                            case["id"],
                            name,
                            repeat,
                            "completed",
                            bool(case["expected_success"]),
                            round(clock.now, 6),
                            "simulated",
                            attempts=mock.call_count,
                            input_tokens=usage.input_tokens if usage else None,
                            output_tokens=usage.output_tokens if usage else None,
                            usage_kind="fixture" if usage else "unavailable",
                            note="correct=True means matched expected recovery outcome",
                        )
                    )
    return records
