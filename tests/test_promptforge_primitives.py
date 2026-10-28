from __future__ import annotations

import pytest

from applied_ai.evaluation import ReadinessCheck, assess_readiness
from applied_ai.orchestration import ReviewFinding, SpecialistReview, synthesize_reviews
from applied_ai.prompting import RequirementGap, select_clarifying_questions


def test_requirement_interview_prioritizes_unanswered_gaps() -> None:
    gaps = (
        RequirementGap("theme", "Choose a theme?", "Presentation only.", 1),
        RequirementGap("identity", "Who may sign in?", "Changes authorization.", 5),
        RequirementGap("storage", "What persists?", "Changes data design.", 4),
    )
    selected = select_clarifying_questions(gaps, answered_areas=("storage",), limit=1)
    assert [gap.area for gap in selected] == ["identity"]
    with pytest.raises(ValueError, match="Question limit"):
        select_clarifying_questions(gaps, limit=9)


def test_specialist_consensus_keeps_highest_severity_and_provenance() -> None:
    consensus = synthesize_reviews(
        (
            SpecialistReview(
                "architecture", (ReviewFinding("Access control", "medium", "Split roles."),)
            ),
            SpecialistReview(
                "security", (ReviewFinding("access  control", "high", "Enforce roles."),)
            ),
        )
    )
    assert consensus[0].severity == "high"
    assert consensus[0].specialists == ("architecture", "security")


def test_readiness_gate_fails_closed_for_blockers() -> None:
    report = assess_readiness((ReadinessCheck("requirements", True),), blockers=("Threat model",))
    assert report.score == 100
    assert not report.ready
    assert report.blockers == ("Threat model",)
