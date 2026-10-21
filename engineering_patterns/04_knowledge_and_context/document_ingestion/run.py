"""Validate external records before they become retrieval documents."""

from applied_ai.knowledge import ingest_records


def main() -> None:
    print(
        [
            document.id
            for document in ingest_records(
                ({"id": "rag", "text": "RAG retrieves context."}, {"id": "rag cc", "text": "xxx."})
            )
        ]
    )


if __name__ == "__main__":
    main()
