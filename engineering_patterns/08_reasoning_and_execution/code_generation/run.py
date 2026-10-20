"""Offline code generation demonstration."""

from applied_ai.reasoning import validate_python_syntax


def main() -> None:
    print(validate_python_syntax("def add(a, b):\n    return a + b"))


if __name__ == "__main__":
    main()
