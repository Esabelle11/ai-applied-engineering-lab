"""Offline mathematical verification demonstration."""

from applied_ai.reasoning import verify_math


def main() -> None:
    print(verify_math("6 * 7", 42))


if __name__ == "__main__":
    main()
