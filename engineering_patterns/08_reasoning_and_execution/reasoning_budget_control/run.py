"""Offline reasoning budget control demonstration."""

from applied_ai.reasoning import within_budget


def main() -> None:
    print(within_budget(3, 5))


if __name__ == "__main__":
    main()
