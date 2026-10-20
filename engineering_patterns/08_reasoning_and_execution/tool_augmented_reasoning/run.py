"""Offline tool augmented reasoning demonstration."""

from applied_ai.reasoning import tool_reason


def main() -> None:
    print(tool_reason("RAG", {"lookup": lambda query: f"definition for {query}"}, "lookup"))


if __name__ == "__main__":
    main()
