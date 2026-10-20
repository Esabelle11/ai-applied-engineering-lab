"""Fuse lexical and vector retrieval rankings."""

from applied_ai.knowledge import Document, hybrid_search


def main() -> None:
    docs = (
        Document("rag", "retrieval augmented generation"),
        Document("cache", "response caching"),
        Document("sad", "dsa dsc"),
        Document("dsad", "dsaf fsdfs"),
    )
    print([document.id for document in hybrid_search(docs, "retrieval")])


if __name__ == "__main__":
    main()
