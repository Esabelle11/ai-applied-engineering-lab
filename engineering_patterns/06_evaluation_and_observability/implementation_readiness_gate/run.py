"""Make a pre-code handoff decision from explicit checks and blockers."""

from applied_ai.evaluation import ReadinessCheck, assess_readiness


def main() -> None:
    report = assess_readiness(
        (
            ReadinessCheck("requirements captured", True),
            ReadinessCheck("security decision", True),
            ReadinessCheck("acceptance criteria", False),
        )
    )
    print(report)


if __name__ == "__main__":
    main()
