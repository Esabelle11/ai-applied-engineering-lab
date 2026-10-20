from __future__ import annotations

import asyncio

from applied_ai.optimization import (
    ModelOption,
    SemanticCache,
    batch_items,
    bounded_map,
    cheapest_qualified,
    compress_text,
    estimate_tokens,
    fastest_qualified,
    pareto_frontier,
)


def test_batch_compress_tokens_and_semantic_cache() -> None:
    assert batch_items((1, 2, 3), size=2) == ((1, 2), (3,))
    assert compress_text("one two three", max_words=2) == "one two"
    assert estimate_tokens("one two.") == 3
    cache = SemanticCache(threshold=1)
    cache.put("rag", "answer")
    assert cache.get("rag") == "answer"


def test_bounded_and_option_selection() -> None:
    assert asyncio.run(
        bounded_map((1, 2), lambda item: asyncio.sleep(0, result=item), max_concurrency=1)
    ) == [1, 2]
    options = (ModelOption("fast", 1, 2, 0.8), ModelOption("cheap", 2, 1, 0.8))
    assert cheapest_qualified(options, minimum_quality=0.8).name == "cheap"
    assert fastest_qualified(options, minimum_quality=0.8).name == "fast"
    assert {item.name for item in pareto_frontier(options)} == {"cheap"}
