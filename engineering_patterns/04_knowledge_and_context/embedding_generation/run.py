"""Generate deterministic hash embeddings for offline retrieval experiments."""

from applied_ai.knowledge import embed_text


def main() -> None:
    print(embed_text("retrieval augmented generation", dimensions=4))


if __name__ == "__main__":
    main()
