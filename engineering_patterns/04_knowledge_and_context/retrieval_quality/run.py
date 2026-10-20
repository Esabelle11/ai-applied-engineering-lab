"""Measure precision and recall for a labelled retrieval result."""

from applied_ai.knowledge import measure_retrieval


def main() -> None:
    print(measure_retrieval(("rag", "cache"), ("rag", "routing"), k=2))


if __name__ == "__main__":
    main()
