"""Transparent implementation-readiness decisions for engineering handoffs."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ReadinessCheck:
    name: str
    passed: bool
    required: bool = True

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Readiness check name cannot be empty")


@dataclass(frozen=True, slots=True)
class ReadinessReport:
    score: int
    ready: bool
    missing_required: tuple[str, ...]
    blockers: tuple[str, ...]


def assess_readiness(
    checks: Sequence[ReadinessCheck], *, blockers: Sequence[str] = ()
) -> ReadinessReport:
    """Score declared checks and fail closed for missing requirements/blockers.

    The score communicates coverage, not a statistical prediction that code
    will succeed. Callers decide which checks are required for their project.
    """
    if not checks:
        raise ValueError("At least one readiness check is required")
    required = tuple(check for check in checks if check.required)
    missing = tuple(check.name for check in required if not check.passed)
    score = round(100 * sum(check.passed for check in checks) / len(checks))
    normalized_blockers = tuple(blocker.strip() for blocker in blockers if blocker.strip())
    return ReadinessReport(
        score, not missing and not normalized_blockers, missing, normalized_blockers
    )
