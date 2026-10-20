"""Rewrite conversational phrasing to a compact retrieval query."""

from applied_ai.knowledge import rewrite_query


def main() -> None:
    print(rewrite_query("Could you tell me retrieval augmented generation?"))


if __name__ == "__main__":
    main()
