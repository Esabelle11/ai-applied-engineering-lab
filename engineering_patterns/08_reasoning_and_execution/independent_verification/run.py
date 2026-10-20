"""Offline independent verification demonstration."""

from applied_ai.reasoning import verify_independently


def main() -> None:
    print(
        verify_independently("42", (lambda value: value.isdigit(), lambda value: int(value) == 42))
    )


if __name__ == "__main__":
    main()
