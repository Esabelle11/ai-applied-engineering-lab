"""Rerank retrieved candidates by explicit query-term overlap."""

from applied_ai.knowledge import Document, rerank


def main() -> None:
    docs = ( Document("notsure", "generation retrieval"), Document("weak", "generation"), Document("strong", "retrieval generation"))
    print([document.id for document in rerank("retrieval generation", docs)])


if __name__ == "__main__":
    main()
