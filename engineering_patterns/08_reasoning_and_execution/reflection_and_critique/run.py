"""Offline reflection and critique demonstration."""

from applied_ai.reasoning import critique


def main() -> None:
    print(critique("The answer is concise.", ("concise", "citation")))


if __name__ == "__main__":
    main()
