"""Offline semantic caching demonstration."""

from applied_ai.optimization import SemanticCache


def main() -> None:
    cache = SemanticCache(threshold=1)
    cache.put("what is rag", "RAG retrieves context")
    print(cache.get("what is rag"))


if __name__ == "__main__":
    main()
