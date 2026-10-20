"""Offline context compression demonstration."""

from applied_ai.optimization import compress_text


def main() -> None:
    print(compress_text("Older conversation context contains redundant details", max_words=4))


if __name__ == "__main__":
    main()
