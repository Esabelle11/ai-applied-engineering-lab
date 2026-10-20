"""Offline stopping conditions demonstration."""

from applied_ai.reasoning import iterate


def main() -> None:
    print(iterate(0, lambda value: value + 1, max_steps=2, stop=lambda value: value >= 5)[1])


if __name__ == "__main__":
    main()
