"""Deterministic helpers for turning requirement gaps into a small interview."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RequirementGap:
    """A missing decision that materially affects implementation."""

    area: str
    question: str
    reason: str
    impact: int

    def __post_init__(self) -> None:
        if not all(value.strip() for value in (self.area, self.question, self.reason)):
            raise ValueError("Requirement gaps need an area, question, and reason")
        if not 1 <= self.impact <= 5:
            raise ValueError("Requirement-gap impact must be from 1 to 5")


def select_clarifying_questions(
    gaps: Sequence[RequirementGap],
    answered_areas: Sequence[str] = (),
    *,
    limit: int = 8,
) -> tuple[RequirementGap, ...]:
    """Choose the highest-impact unanswered questions with stable ordering.

    An application may use an LLM to discover gaps. This function owns only
    the deterministic policy: do not repeat answered areas and keep the
    interview short enough for a human to complete.
    """
    if not 1 <= limit <= 8:
        raise ValueError("Question limit must be between 1 and 8")
    answered = {area.casefold().strip() for area in answered_areas}
    pending = (gap for gap in gaps if gap.area.casefold() not in answered)
    return tuple(sorted(pending, key=lambda gap: -gap.impact)[:limit])


def merge_requirement_answers(
    answers: Mapping[str, str], questions: Sequence[RequirementGap]
) -> dict[str, str]:
    """Keep only non-empty answers for questions selected for this interview."""
    allowed = {question.area for question in questions}
    return {
        area: answer.strip()
        for area, answer in answers.items()
        if area in allowed and isinstance(answer, str) and answer.strip()
    }
