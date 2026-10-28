"""Choose a short, high-value requirements interview without model calls."""

from applied_ai.prompting import (
    RequirementGap,
    merge_requirement_answers,
    select_clarifying_questions,
)


def main() -> None:
    gaps = (
        RequirementGap("authentication", "Which users may sign in?", "Changes access control.", 5),
        RequirementGap("database", "What data must persist?", "Changes storage design.", 5),
        RequirementGap(
            "theme", "Which colour palette is preferred?", "Changes presentation only.", 1
        ),
    )
    questions = select_clarifying_questions(gaps, answered_areas=("theme",))
    answers = merge_requirement_answers(
        {"authentication": "Company SSO", "database": "Incidents and owners"}, questions
    )
    print([question.area for question in questions])
    print(answers)


if __name__ == "__main__":
    main()
