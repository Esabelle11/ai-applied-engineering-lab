"""Check that an answer's citations name supplied context sources."""

from applied_ai.knowledge import citations_supported


def main() -> None:
    print(citations_supported("RAG retrieves context [rag-doc].", ("rag-doc",)))


if __name__ == "__main__":
    main()
