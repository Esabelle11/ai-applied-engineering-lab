"""Deterministic and fully offline Phase 3 SDK contracts and runnable patterns."""

from __future__ import annotations

import asyncio
import os
import subprocess
import sys
from pathlib import Path

import pytest

from applied_ai import LLMRequest, Message, MockProvider, StructuredOutputSpec
from applied_ai.core.exceptions import CapabilityNotSupportedError, InvalidStructuredOutputError
from applied_ai.evaluation import EvalCase, evaluate, exact_match
from applied_ai.inference import generate_concurrently
from applied_ai.knowledge import Document, LexicalRetriever, answer_with_context
from applied_ai.optimization import CachingProvider
from applied_ai.orchestration import GraphNode, StateGraph
from applied_ai.prompting import PromptChain, PromptStep, PromptTemplate
from applied_ai.reasoning import VerificationLoop
from applied_ai.routing import ModelTarget, TaskRouter

ROOT = Path(__file__).resolve().parents[1]
NEW_PATTERNS = (
    "02_model_integration/multi_model_routing",
    "02_model_integration/async_inference",
    "02_model_integration/model_capability_detection",
    "01_prompt_engineering/prompt_chaining",
    "01_prompt_engineering/structured_outputs",
    "05_reliability_engineering/exponential_backoff",
    "03_agent_orchestration/graph_workflows",
    "04_knowledge_and_context/rag_pipelines",
    "08_reasoning_and_execution/plan_execute_verify",
    "06_evaluation_and_observability/response_quality",
    "07_optimization/response_caching",
)


def request(text: str = "Hi") -> LLMRequest:
    return LLMRequest("original", (Message("user", text),))


def test_routing_explicit_model_id_and_task() -> None:
    primary = MockProvider(default_text="one")
    router = TaskRouter({"fast": ModelTarget(primary, "model-fast")})
    assert router.generate("fast", request()).model == "model-fast"
    assert router.generate("fast", request()).text == "one"
    with pytest.raises(ValueError, match="Unconfigured route"):
        router.generate("unknown", request())
    with pytest.raises(ValueError):
        ModelTarget(primary, " ")


def test_routing_rejects_incompatible_structured_output() -> None:
    provider = MockProvider(supports_structured_output=False)
    router = TaskRouter({"json": ModelTarget(provider, "mock")})
    structured = LLMRequest(
        "original",
        (Message("user", "json"),),
        response_format=StructuredOutputSpec("answer", {"type": "object"}),
    )
    with pytest.raises(CapabilityNotSupportedError):
        router.generate("json", structured)
    assert provider.call_count == 0


def test_async_adapter_returns_results_in_input_order() -> None:
    provider = MockProvider(responses={"A": "one", "B": "two"})
    results = asyncio.run(
        generate_concurrently(provider, [request("A"), request("B")], max_concurrency=2)
    )
    assert [result.text for result in results] == ["one", "two"]
    with pytest.raises(ValueError):
        asyncio.run(generate_concurrently(provider, [request("A")], max_concurrency=0))


def test_template_requires_declared_simple_string_variables() -> None:
    assert PromptTemplate("Hello {name}").render({"name": "Ada"}) == "Hello Ada"
    with pytest.raises(ValueError, match="Missing"):
        PromptTemplate("Hello {name}").render({})
    with pytest.raises(ValueError, match="simple placeholders"):
        PromptTemplate("{person.name}").render({"person.name": "Ada"})
    with pytest.raises(TypeError):
        PromptTemplate("{name}").render({"name": 42})  # type: ignore[dict-item]


def test_prompt_chain_and_invalid_step_names() -> None:
    provider = MockProvider(responses={"Summarize RAG": "context", "Shorten context": "RAG"})
    chain = PromptChain(
        [
            PromptStep("summary", PromptTemplate("Summarize {topic}")),
            PromptStep("short", PromptTemplate("Shorten {summary}")),
        ]
    )
    assert chain.run(provider, "mock", {"topic": "RAG"})["short"] == "RAG"
    assert provider.call_count == 2
    with pytest.raises(ValueError):
        PromptChain([PromptStep("bad-name!", PromptTemplate("x"))])
    with pytest.raises(ValueError):
        PromptChain([PromptStep("x", PromptTemplate("1")), PromptStep("x", PromptTemplate("2"))])


def test_structured_output_reuses_core_validator() -> None:
    fmt = StructuredOutputSpec(
        "result",
        {
            "type": "object",
            "properties": {"n": {"type": "integer"}},
            "required": ["n"],
            "additionalProperties": False,
        },
    )
    req = LLMRequest("mock", (Message("user", "return json"),), response_format=fmt)
    assert MockProvider(default_text='{"n": 4}').generate(req).parsed_output == {"n": 4}
    with pytest.raises(InvalidStructuredOutputError):
        MockProvider(default_text='{"n": "4"}').generate(req)


def test_graph_resume_and_boundaries() -> None:
    graph = StateGraph(
        {
            "a": GraphNode(lambda _: ({"step": "done"}, "b")),
            "b": GraphNode(lambda _: ({"answer": "42"}, None)),
        },
        start="a",
    )
    snapshot = graph.execute({}, max_steps=1)
    assert snapshot.next_node == "b"
    assert not snapshot.completed
    result = graph.execute(snapshot)
    assert result.completed and result.data["answer"] == "42"
    assert result.history == ("a", "b")
    assert "answer" not in snapshot.data
    with pytest.raises(TypeError):
        snapshot.data["tamper"] = "yes"  # type: ignore[index]
    with pytest.raises(ValueError, match="max_steps"):
        graph.execute({}, max_steps=0)


def test_graph_rejects_unknown_next_node_and_bad_state() -> None:
    with pytest.raises(ValueError):
        StateGraph({}, "missing")
    bad_destination = StateGraph({"a": GraphNode(lambda _: ({}, "missing"))}, "a")
    with pytest.raises(ValueError, match="Unknown"):
        bad_destination.execute({})
    bad_updates = StateGraph({"a": GraphNode(lambda _: ({"count": 1}, None))}, "a")
    with pytest.raises(TypeError):
        bad_updates.execute({})


def test_lexical_retrieval_order_no_hits_and_id_uniqueness() -> None:
    data = [Document("rag", "retrieval augmented generation"), Document("other", "cats purr")]
    searcher = LexicalRetriever(data)
    assert [doc.id for doc in searcher.search("retrieval augmented")] == ["rag"]
    assert searcher.search("unknownkeyword") == ()
    with pytest.raises(ValueError):
        searcher.search("retrieval", limit=0)
    with pytest.raises(ValueError):
        LexicalRetriever([data[0], data[0]])
    with pytest.raises(LookupError):
        answer_with_context(MockProvider(), "mock", searcher, "unknownkeyword")


def test_knowledge_answer_tracks_sources() -> None:
    documents = LexicalRetriever([Document("reference", "retrieval augmented generation")])
    answer = answer_with_context(
        MockProvider(default_text="The answer [reference]."),
        "mock",
        documents,
        "retrieval augmented generation",
    )
    assert answer.retrieved_ids == ("reference",)
    assert answer.response.text == "The answer [reference]."


def test_bounded_verification_success_and_failure() -> None:
    q = "Compute 6 times 7"
    retry = "Previous answer failed independent verification. Try again."
    provider = MockProvider(responses={q: "41", f"{q}\n{retry}": "42"})
    result = VerificationLoop(provider, "mock", max_attempts=2).solve(
        q, lambda value: value == "42"
    )
    assert (result.accepted, result.attempts) == (True, 2)
    result = VerificationLoop(MockProvider(default_text="wrong"), "mock", max_attempts=2).solve(
        q, lambda value: value == "42"
    )
    assert not result.accepted and result.attempts == 2
    with pytest.raises(ValueError):
        VerificationLoop(provider, "mock", max_attempts=0)


def test_exact_match_evaluation_has_explicit_denominator() -> None:
    cases = [EvalCase("q1", "42"), EvalCase("q2", "true")]
    results = {"q1": " 42 ", "q2": "FALSE"}
    report = evaluate(cases, lambda q: results[q])
    assert (report.passed, report.total, report.accuracy) == (1, 2, 0.5)
    assert report.failed_questions == ("q2",)
    assert evaluate([], lambda _: "unused").accuracy == 0.0
    assert exact_match("A    B", "a b")


def test_cache_hits_key_changes_expiry_and_errors() -> None:
    class Clock:
        value = 0.0

        def __call__(self) -> float:
            return self.value

    clock = Clock()
    backend = MockProvider(default_text="cache")
    cache = CachingProvider(backend, ttl_seconds=2, clock=clock)
    assert not cache.generate_with_cache_info(request("A")).hit
    assert cache.generate_with_cache_info(request("A")).hit
    assert backend.call_count == 1
    assert not cache.generate_with_cache_info(request("B")).hit
    assert backend.call_count == 2
    clock.value = 3
    assert not cache.generate_with_cache_info(request("A")).hit
    assert backend.call_count == 3
    with pytest.raises(ValueError):
        CachingProvider(backend, ttl_seconds=0)
    with pytest.raises(ValueError):
        CachingProvider(backend, ttl_seconds=float("nan"))


@pytest.mark.parametrize("pattern", NEW_PATTERNS)
def test_every_published_phase3_example_runs_offline(pattern: str) -> None:
    path = ROOT / "engineering_patterns" / pattern
    env = dict(os.environ)
    env.pop("OPENAI_API_KEY", None)
    # Same environment works in a clean checkout with an installed editable package.
    result = subprocess.run(
        [sys.executable, str(path / "run.py")],
        capture_output=True,
        text=True,
        check=False,
        timeout=15,
        env=env,
    )
    assert result.returncode == 0, (pattern, result.stderr)
    assert result.stdout.strip(), pattern
    assert (path / "README.md").is_file()
    assert (path / "pattern.yaml").is_file()
