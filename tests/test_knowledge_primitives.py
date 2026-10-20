from __future__ import annotations

import pytest

from applied_ai.knowledge import (
    Document,
    LongTermMemory,
    VectorRetriever,
    build_context,
    chunk_text,
    citations_supported,
    embed_text,
    hybrid_search,
    ingest_records,
    measure_retrieval,
    rerank,
    rewrite_query,
)


def test_ingestion_chunking_and_deterministic_embeddings() -> None:
    documents = ingest_records(({"id": "one", "text": "retrieval augmented generation"},))
    assert documents[0].id == "one"
    assert chunk_text("abcdefgh", max_chars=4, overlap=1) == ("abcd", "defg", "gh")
    assert embed_text("retrieval", dimensions=4) == embed_text("retrieval", dimensions=4)
    with pytest.raises(ValueError):
        ingest_records(({"id": "one", "text": "a"}, {"id": "one", "text": "b"}))


def test_vector_hybrid_and_rerank_results_are_stable() -> None:
    documents = (Document("rag", "retrieval augmented generation"), Document("cats", "cats purr"))
    assert VectorRetriever(documents).search("retrieval")[0].id == "rag"
    assert hybrid_search(documents, "retrieval")[0].id == "rag"
    assert rerank("retrieval generation", documents)[0].id == "rag"


def test_context_memory_grounding_and_metrics() -> None:
    window = build_context((Document("one", "short"), Document("two", "longer source")), max_chars=14)
    assert window.included_ids == ("one",)
    assert window.omitted_ids == ("two",)
    assert rewrite_query("Could you tell me RAG?") == "RAG"

    memory = LongTermMemory()
    memory.remember("pref", "prefers concise answers")
    assert memory.recall("concise")[0].id == "pref"
    assert citations_supported("Answer [one]", ("one",))
    assert not citations_supported("Answer [missing]", ("one",))
    metrics = measure_retrieval(("one", "two"), ("one", "three"), k=2)
    assert (metrics.precision_at_k, metrics.recall_at_k) == (0.5, 0.5)
