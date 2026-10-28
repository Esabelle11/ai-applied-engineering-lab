"""Deterministic offline response quality evaluation."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EvalCase:
    question: str
    expected: str


@dataclass(frozen=True, slots=True)
class EvalReport:
    passed: int
    total: int
    failed_questions: tuple[str, ...]

    @property
    def accuracy(self) -> float:
        return self.passed / self.total if self.total else 0.0


def exact_match(actual: str, expected: str) -> bool:
    """Case/whitespace-normalized exact match; not semantic equivalence."""
    return " ".join(actual.lower().split()) == " ".join(expected.lower().split())


def evaluate(cases: Sequence[EvalCase], predict: Callable[[str], str]) -> EvalReport:
    failed = tuple(
        case.question for case in cases if not exact_match(predict(case.question), case.expected)
    )
    return EvalReport(len(cases) - len(failed), len(cases), failed)


# These re-exports must follow exact_match: observability imports it from this
# public module. They intentionally form the package's stable convenience API.
from applied_ai.evaluation.observability import (  # noqa: E402, F401
    DatasetItem,
    TraceEvent,
    TraceLog,
    benchmark,
    estimate_cost,
    failure_counts,
    grounded,
    judge_response,
    regressions,
    retrieval_recall,
    score_dataset,
    token_total,
    tool_call_passed,
)
from applied_ai.evaluation.readiness import (  # noqa: E402, F401
    ReadinessCheck,
    ReadinessReport,
    assess_readiness,
)
