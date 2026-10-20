"""Build a bounded context window and report excluded sources."""

from applied_ai.knowledge import Document, build_context


def main() -> None:
    window = build_context(
        (Document("a", "short source"), Document("b", "another source")), max_chars=30
    )
    print(window)


if __name__ == "__main__":
    main()
