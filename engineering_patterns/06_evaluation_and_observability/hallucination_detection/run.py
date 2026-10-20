"""Offline hallucination detection demonstration."""

from applied_ai.evaluation import grounded


def main() -> None:
    print(grounded("RAG retrieves context [rag].", ("rag",)))


if __name__ == "__main__":
    main()
