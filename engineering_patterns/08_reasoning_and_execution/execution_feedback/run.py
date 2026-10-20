"""Offline execution feedback demonstration."""

from applied_ai.reasoning import critique


def main() -> None:
    print(critique("Answer with source", ("source", "number")))


if __name__ == "__main__":
    main()
