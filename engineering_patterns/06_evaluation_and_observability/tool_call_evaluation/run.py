"""Offline tool call evaluation demonstration."""

from applied_ai.evaluation import tool_call_passed


def main() -> None:
    print(tool_call_passed("lookup", {"id": "1"}, {"lookup"}))


if __name__ == "__main__":
    main()
