"""Executable, offline Applied AI handbook pattern."""

from applied_ai import MockProvider
from applied_ai.knowledge import Document, LexicalRetriever, answer_with_context


def main() -> None:
    docs = [
        Document("rag", "Retrieval augmented generation combines retrieval and generation."),
        Document("cats", "Cats often purr."),
    ]
    retriever = LexicalRetriever(docs)
    answer = answer_with_context(
        MockProvider(default_text="RAG uses retrieved information [rag]."),
        "mock",
        retriever,
        "What is retrieval augmented generation?",
    )
    print(f"Sources: {answer.retrieved_ids}; answer: {answer.response.text}")


if __name__ == "__main__":
    main()
