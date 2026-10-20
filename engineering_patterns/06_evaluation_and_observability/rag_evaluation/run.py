"""Offline rag evaluation demonstration."""

from applied_ai.evaluation import retrieval_recall


def main() -> None:
    print(retrieval_recall(("rag","cache"), ("rag",), k=2))


if __name__ == "__main__":
    main()
