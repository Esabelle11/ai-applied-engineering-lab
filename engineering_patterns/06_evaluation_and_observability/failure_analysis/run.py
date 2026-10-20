"""Offline failure analysis demonstration."""

from applied_ai.evaluation import failure_counts


def main() -> None:
    print(failure_counts(("timeout", "timeout", "rate_limit")))


if __name__ == "__main__":
    main()
