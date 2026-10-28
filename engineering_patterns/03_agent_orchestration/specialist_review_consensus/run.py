"""Merge overlapping architecture, security, and QA review findings."""

from applied_ai.orchestration import ReviewFinding, SpecialistReview, synthesize_reviews


def main() -> None:
    reviews = (
        SpecialistReview(
            "architecture",
            (ReviewFinding("Role boundaries", "medium", "Separate admin actions."),),
        ),
        SpecialistReview(
            "security",
            (ReviewFinding("role  boundaries", "high", "Enforce server-side authorization."),),
        ),
    )
    for finding in synthesize_reviews(reviews):
        print(f"{finding.severity}: {finding.title} ({', '.join(finding.specialists)})")


if __name__ == "__main__":
    main()
