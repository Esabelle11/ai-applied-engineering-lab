"""Retrieve documents using deterministic vector similarity."""

from applied_ai.knowledge import Document, VectorRetriever


def main() -> None:
    docs = (Document("rag", "retrieval augmented generation"), Document("cats", "cats purr"),Document("dogs", "dogs purr"),Document("apples", "apple purr"))
    print([document.id for document in VectorRetriever(docs).search("retrieval context")])


if __name__ == "__main__":
    main()
