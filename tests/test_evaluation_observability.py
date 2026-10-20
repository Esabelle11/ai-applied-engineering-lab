from __future__ import annotations

import pytest

from applied_ai import TokenUsage
from applied_ai.evaluation import (
    DatasetItem,
    TraceLog,
    estimate_cost,
    failure_counts,
    grounded,
    regressions,
    retrieval_recall,
    score_dataset,
    tool_call_passed,
)


def test_evaluation_metrics_and_regression_helpers() -> None:
    assert score_dataset((DatasetItem("one", "q", "a"),), lambda _: "a") == 1
    assert retrieval_recall(("a",), ("a", "b"), k=1) == 0.5
    assert grounded("fact [a]", ("a",))
    assert tool_call_passed("lookup", {"id": "1"}, {"lookup"})
    assert regressions({"a": "one"}, {"a": "two"}) == ("a",)
    assert failure_counts(("timeout", "timeout")) == {"timeout": 2}


def test_costs_and_traces_are_explicit() -> None:
    assert (
        estimate_cost(
            TokenUsage(input_tokens=2, output_tokens=3), input_per_token=1, output_per_token=2
        )
        == 8
    )
    with pytest.raises(ValueError):
        estimate_cost(TokenUsage(), input_per_token=-1, output_per_token=0)
    trace = TraceLog()
    trace.add("request", model="mock")
    assert trace.snapshot()[0].attributes == {"model": "mock"}
