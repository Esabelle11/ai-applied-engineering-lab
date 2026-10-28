"""Deterministic synthesis of findings from named specialist reviews."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

_SEVERITIES = {"critical": 4, "high": 3, "medium": 2, "low": 1}


@dataclass(frozen=True, slots=True)
class ReviewFinding:
    title: str
    severity: str
    recommendation: str

    def __post_init__(self) -> None:
        if not self.title.strip() or not self.recommendation.strip():
            raise ValueError("Review findings need a title and recommendation")
        if self.severity not in _SEVERITIES:
            raise ValueError("Unknown review severity")


@dataclass(frozen=True, slots=True)
class SpecialistReview:
    specialist: str
    findings: tuple[ReviewFinding, ...]

    def __post_init__(self) -> None:
        if not self.specialist.strip():
            raise ValueError("A specialist review needs a name")


@dataclass(frozen=True, slots=True)
class ConsensusFinding:
    title: str
    severity: str
    recommendation: str
    specialists: tuple[str, ...]


def synthesize_reviews(reviews: Sequence[SpecialistReview]) -> tuple[ConsensusFinding, ...]:
    """Deduplicate named findings, retain the highest severity, then prioritize.

    Equal normalized titles represent the same decision. A production workflow
    should let an engineering lead resolve semantic conflicts; this helper
    makes the mechanical merge predictable and keeps reviewer provenance.
    """
    if not reviews:
        raise ValueError("At least one specialist review is required")
    merged: dict[str, list[object]] = {}
    for review in reviews:
        for finding in review.findings:
            key = " ".join(finding.title.casefold().split())
            current = merged.get(key)
            if current is None:
                merged[key] = [finding, [review.specialist]]
                continue
            chosen, specialists = current
            assert isinstance(chosen, ReviewFinding) and isinstance(specialists, list)
            if _SEVERITIES[finding.severity] > _SEVERITIES[chosen.severity]:
                current[0] = ReviewFinding(chosen.title, finding.severity, finding.recommendation)
            if review.specialist not in specialists:
                specialists.append(review.specialist)

    findings = []
    for chosen, specialists in merged.values():
        assert isinstance(chosen, ReviewFinding) and isinstance(specialists, list)
        findings.append(
            ConsensusFinding(
                title=chosen.title,
                severity=chosen.severity,
                recommendation=chosen.recommendation,
                specialists=tuple(specialists),
            )
        )
    return tuple(
        sorted(findings, key=lambda finding: (-_SEVERITIES[finding.severity], finding.title))
    )
