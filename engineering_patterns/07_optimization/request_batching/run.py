"""Offline request batching demonstration."""

from applied_ai.optimization import batch_items


def main() -> None:
    print(batch_items((1, 2, 3, 4, 5), size=2))


if __name__ == "__main__":
    main()
