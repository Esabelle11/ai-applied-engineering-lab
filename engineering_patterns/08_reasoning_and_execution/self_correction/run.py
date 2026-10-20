"""Offline self correction demonstration."""

from applied_ai.reasoning import critique


def main() -> None:
    answer = "Answer"
    print(answer + " [source]" if critique(answer, ("source",)) else answer)


if __name__ == "__main__":
    main()
