"""Split long text into bounded, overlapping context chunks."""

from applied_ai.knowledge import chunk_text


def main() -> None:
    print(chunk_text("abcdefghij", max_chars=4, overlap=1))


if __name__ == "__main__":
    main()
