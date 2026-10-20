"""Offline iterative reasoning demonstration."""

from applied_ai.reasoning import iterate


def main() -> None:
    print(iterate(0, lambda value: value + 1, max_steps=5, stop=lambda value: value == 3))


if __name__ == "__main__":
    main()
