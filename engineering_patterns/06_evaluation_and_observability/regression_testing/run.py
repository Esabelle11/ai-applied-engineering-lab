"""Offline regression testing demonstration."""

from applied_ai.evaluation import regressions


def main() -> None:
    print(regressions({"case": "expected"}, {"case": "expected"}))


if __name__ == "__main__":
    main()
