"""Offline prompt compression demonstration."""

from applied_ai.optimization import compress_text


def main() -> None:
    print(compress_text("Explain retrieval augmented generation with sources", max_words=3))


if __name__ == "__main__":
    main()
