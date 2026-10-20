"""Deterministic evaluation and observability helpers for offline examples."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from time import monotonic

from applied_ai.core.responses import TokenUsage
from applied_ai.evaluation import exact_match


@dataclass(frozen=True, slots=True)
class DatasetItem:
    identifier: str
    input: str
    expected: str

    def __post_init__(self) -> None:
        if not all(value.strip() for value in (self.identifier, self.input, self.expected)):
            raise ValueError("Dataset values must be non-empty")


def score_dataset(items: Sequence[DatasetItem], predict: Callable[[str], str]) -> float:
    if not items:
        raise ValueError("Dataset cannot be empty")
    return sum(exact_match(predict(item.input), item.expected) for item in items) / len(items)


def judge_response(response: str, rubric: Callable[[str], bool]) -> bool:
    if not response.strip():
        raise ValueError("Response cannot be empty")
    return bool(rubric(response))


def retrieval_recall(retrieved: Sequence[str], relevant: Sequence[str], *, k: int) -> float:
    if not relevant or k < 1:
        raise ValueError("Relevant IDs and positive k are required")
    return len(set(retrieved[:k]) & set(relevant)) / len(set(relevant))


def grounded(answer: str, source_ids: Sequence[str]) -> bool:
    return all(f"[{source}]" in answer for source in source_ids)


def benchmark(operation: Callable[[], object], *, clock: Callable[[], float] = monotonic) -> float:
    started = clock()
    operation()
    return clock() - started


def token_total(usage: TokenUsage | None) -> int | None:
    return None if usage is None else usage.total_tokens


def estimate_cost(usage: TokenUsage, *, input_per_token: float, output_per_token: float) -> float:
    if min(input_per_token, output_per_token) < 0:
        raise ValueError("Rates cannot be negative")
    return (usage.input_tokens or 0) * input_per_token + (
        usage.output_tokens or 0
    ) * output_per_token


def tool_call_passed(name: str, arguments: Mapping[str, object], allowed: set[str]) -> bool:
    return bool(name) and name in allowed and bool(arguments)


def regressions(baseline: Mapping[str, str], current: Mapping[str, str]) -> tuple[str, ...]:
    return tuple(
        key
        for key in sorted(baseline)
        if key not in current or not exact_match(baseline[key], current[key])
    )


def failure_counts(categories: Sequence[str]) -> Mapping[str, int]:
    return dict(Counter(category for category in categories if category))


@dataclass(frozen=True, slots=True)
class TraceEvent:
    name: str
    attributes: Mapping[str, str]

    def __post_init__(self) -> None:
        if not self.name.strip() or not all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in self.attributes.items()
        ):
            raise ValueError("Trace data must contain string names and attributes")


class TraceLog:
    def __init__(self) -> None:
        self._events: list[TraceEvent] = []

    def add(self, name: str, **attributes: str) -> None:
        self._events.append(TraceEvent(name, attributes))

    def snapshot(self) -> tuple[TraceEvent, ...]:
        return tuple(self._events)
