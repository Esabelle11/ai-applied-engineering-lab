"""Curated, bounded playground recipes composed from the existing SDK.

No shell execution, no arbitrary module imports, no Docker access, no generated code.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter
from typing import Any

import yaml

from applied_ai.core import LLMRequest, Message
from applied_ai.core.exceptions import RateLimitError
from applied_ai.knowledge import Document, LexicalRetriever, answer_with_context
from applied_ai.orchestration import GraphNode, StateGraph
from applied_ai.prompting import PromptTemplate
from applied_ai.providers.factory import ProviderFactory
from applied_ai.providers.mock import MockProvider
from applied_ai.reasoning import VerificationLoop
from applied_ai.reliability import ReliableProvider, RetryPolicy

ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class ExampleSpec:
    id: str
    title: str
    category: str
    summary: str
    parameter_name: str
    placeholder: str
    default: str
    live_supported: bool = False


EXAMPLES = (
    ExampleSpec(
        "generation",
        "Provider-neutral generation",
        "02 Model Integration",
        "Same request/response contract with a mock or an opt-in live provider.",
        "prompt",
        "Ask a short question",
        "What is retrieval-augmented generation?",
        True,
    ),
    ExampleSpec(
        "prompt_template",
        "Prompt template",
        "01 Prompt Engineering",
        "Render a bounded reusable template then generate a response.",
        "topic",
        "Enter a topic",
        "vector retrieval",
        True,
    ),
    ExampleSpec(
        "retry",
        "Recover from a transient failure",
        "05 Reliability Engineering",
        "A simulated rate limit is retried using the SDK reliability wrapper.",
        "prompt",
        "Short request",
        "Explain exponential backoff.",
    ),
    ExampleSpec(
        "grounded_retrieval",
        "Source-aware retrieval",
        "04 Knowledge & Context",
        "Lexical search over synthetic public-help documents; source identifiers included.",
        "question",
        "Try: passport renewal",
        "How do I renew a passport?",
    ),
    ExampleSpec(
        "state_graph",
        "Agent state graph",
        "03 Agent Orchestration",
        "Pass state across three bounded nodes without external tools.",
        "topic",
        "Debate topic",
        "Should schools teach coding?",
    ),
    ExampleSpec(
        "verification",
        "Bounded verification loop",
        "08 Reasoning & Execution",
        "A scripted incorrect answer is rejected before a correct answer is accepted.",
        "question",
        "Math task (demo uses 17 × 23 + 9)",
        "Compute 17 * 23 + 9",
    ),
)
INDEX = {example.id: example for example in EXAMPLES}


def discover_patterns() -> list[dict[str, Any]]:
    """Read handbook manifests for discovery only; never execute their entrypoints."""
    results: list[dict[str, Any]] = []
    for path in sorted((ROOT / "engineering_patterns").glob("0[1-8]_*/**/pattern.yaml")):
        if path.parent.parent.name.startswith("_"):
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            continue
        results.append(
            {
                "id": str(data.get("id", "")),
                "name": str(data.get("name", "")),
                "category": path.parent.parent.name,
                "status": str(data.get("status", "")),
                "offline": bool(data.get("supports_offline_testing", False)),
                "playground_example": next(
                    (
                        e.id
                        for e in EXAMPLES
                        if (
                            (e.id == "generation" and path.parent.name == "basic_api_integration")
                            or (e.id == "retry" and path.parent.name == "retry_mechanisms")
                            or (
                                e.id == "prompt_template" and path.parent.name == "prompt_templates"
                            )
                            or (
                                e.id == "grounded_retrieval"
                                and path.parent.name == "lexical_retrieval"
                            )
                        )
                    ),
                    None,
                ),
            }
        )
    return results


def _result(
    *,
    example: str,
    input_text: str,
    output: str,
    provider: str = "mock",
    model: str = "mock-model",
    attempts: int = 1,
    trace: list[dict[str, Any]] | None = None,
    validation: dict[str, Any] | None = None,
    tokens: dict[str, Any] | None = None,
    elapsed: float = 0.0,
    notes: str = "Synthetic offline demonstration",
) -> dict[str, Any]:
    return {
        "example": example,
        "input": input_text,
        "output": output,
        "provider": provider,
        "model": model,
        "attempts": attempts,
        "latency_ms": round(elapsed * 1000, 3),
        "latency_kind": "observed_wall",
        "trace": trace or [],
        "validation": validation or {"status": "not_evaluated"},
        "usage": tokens,
        "cost_usd": None,
        "cost_note": "Unavailable; not assumed zero",
        "notes": notes,
    }


def _live_generate(example: str, text: str) -> dict[str, Any]:
    selected = ProviderFactory(dotenv=ROOT / ".env").create(allow_live=True)
    provider = selected.provider
    try:
        if provider.name == "mock":
            raise ValueError("Live mode requires a non-mock provider in .env")
        response = provider.generate(
            LLMRequest(
                selected.model,
                (Message("user", text),),
                # Reasoning models may spend output budget before emitting text.
                # Keep enough headroom for both reasoning and the bounded reply.
                max_output_tokens=512,
                timeout_seconds=15,
            )
        )
        usage = asdict(response.usage) if response.usage is not None else None
        return _result(
            example=example,
            input_text=text,
            output=response.text,
            provider=response.provider,
            model=response.model,
            tokens=usage,
            elapsed=response.latency_seconds or 0,
            trace=[{"step": "provider.generate", "status": "completed", "kind": "live"}],
            notes="Opt-in live response; no quality guarantee. Cost not calculated.",
        )
    finally:
        close = getattr(provider, "close", None)
        if callable(close):
            close()


def execute(example_id: str, value: str, *, live: bool = False) -> dict[str, Any]:
    """Whitelisted, bounded SDK calls; never call arbitrary Python from user content."""
    if example_id not in INDEX:
        raise ValueError("Unknown executable example")
    if not isinstance(value, str) or not value.strip() or len(value) > 500:
        raise ValueError("Input must contain 1–500 characters")
    value = value.strip()
    if live:
        if not INDEX[example_id].live_supported:
            raise ValueError("Live mode is not supported for this example")
        text = (
            PromptTemplate("Explain {topic} in one concise sentence.").render({"topic": value})
            if example_id == "prompt_template"
            else value
        )
        return _live_generate(example_id, text)

    start = perf_counter()
    if example_id == "generation":
        response = MockProvider(
            default_text="A language model uses retrieved passages to ground its reply."
        ).generate(LLMRequest("mock-model", (Message("user", value),)))
        return _result(
            example=example_id,
            input_text=value,
            output=response.text,
            elapsed=perf_counter() - start,
            trace=[{"step": "MockProvider.generate", "status": "completed"}],
            validation={"status": "passed", "check": "response_nonempty"},
        )

    if example_id == "prompt_template":
        prompt = PromptTemplate("Explain {topic} in one concise sentence.").render({"topic": value})
        response = MockProvider(
            default_text="Templates separate reusable instructions from task variables."
        ).generate(LLMRequest("mock-model", (Message("user", prompt),)))
        return _result(
            example=example_id,
            input_text=prompt,
            output=response.text,
            elapsed=perf_counter() - start,
            trace=[
                {"step": "PromptTemplate.render", "status": "completed"},
                {"step": "MockProvider.generate", "status": "completed"},
            ],
        )

    if example_id == "retry":
        provider = MockProvider(
            default_text="Recovered after one rate-limit failure.",
            faults=[RateLimitError("synthetic 429")],
        )
        wrapper = ReliableProvider(
            provider,
            policy=RetryPolicy(
                max_attempts=2,
                initial_delay_seconds=0,
                jitter=False,
            ),
        )
        reply = wrapper.generate(LLMRequest("mock-model", (Message("user", value),)))
        assert reply.reliability is not None
        return _result(
            example=example_id,
            input_text=value,
            output=reply.text,
            elapsed=perf_counter() - start,
            attempts=reply.reliability.attempts,
            trace=[
                {"step": "provider.generate", "status": "rate_limit", "attempt": 1},
                {"step": "provider.generate", "status": "completed", "attempt": 2},
            ],
            validation={"status": "passed", "check": "retry_recovery"},
        )

    if example_id == "grounded_retrieval":
        retriever = LexicalRetriever(
            (
                Document(
                    "HELP-1", "Passport renewal requires an appointment and identity verification."
                ),
                Document("HELP-2", "Lost cards should be reported to the issuing bank promptly."),
                Document("HELP-3", "Permit applications require supporting documents."),
            )
        )
        matched = retriever.search(value)
        if not matched:
            raise LookupError("No matching source documents")
        fixture_reply = f"{matched[0].text} [{matched[0].id}]"
        answer = answer_with_context(
            MockProvider(default_text=fixture_reply), "mock-model", retriever, value
        )
        citations = re.findall(r"\[(HELP-\d+)\]", answer.response.text)
        valid_ids = bool(citations) and all(c in answer.retrieved_ids for c in citations)
        return _result(
            example=example_id,
            input_text=value,
            output=answer.response.text,
            elapsed=perf_counter() - start,
            trace=[
                {
                    "step": "LexicalRetriever.search",
                    "status": "completed",
                    "source_ids": list(answer.retrieved_ids),
                },
                {"step": "MockProvider.generate", "status": "completed"},
            ],
            validation={
                "status": "passed" if valid_ids else "failed",
                "source_ids": list(answer.retrieved_ids),
                "cited_ids": citations,
                "note": "Citation ID check only; semantic grounding not established",
            },
        )

    if example_id == "state_graph":
        graph = StateGraph(
            {
                "opening": GraphNode(
                    lambda state: ({"opening": f"Opening question: {state['topic']}"}, "counter")
                ),
                "counter": GraphNode(
                    lambda _: (
                        {"counter": "Counterpoint: consider potential drawbacks."},
                        "summary",
                    )
                ),
                "summary": GraphNode(
                    lambda _: (
                        {"summary": "Compare the strongest arguments before deciding."},
                        None,
                    )
                ),
            },
            start="opening",
        )
        snapshot = graph.execute({"topic": value}, max_steps=3)
        return _result(
            example=example_id,
            input_text=value,
            output="\n".join(snapshot.data[node] for node in snapshot.history),
            elapsed=perf_counter() - start,
            trace=[{"step": step, "status": "completed"} for step in snapshot.history],
            validation={
                "status": "passed" if snapshot.completed else "failed",
                "check": "graph_completion",
            },
        )

    if example_id == "verification":
        # Deliberately scoped to a fixed, independent arithmetic fixture.
        # No user-supplied Python or model-generated code executes in the server.
        if value not in {"Compute 17 * 23 + 9", "Compute 17 * 23 + 9."}:
            raise ValueError("This demonstration supports only: Compute 17 * 23 + 9")

        class ScriptedMock(MockProvider):
            def generate(self, request: LLMRequest) -> Any:
                self.call_count += 1
                from applied_ai.core.responses import LLMResponse

                return LLMResponse(
                    "401" if self.call_count == 1 else "400", request.model, self.name
                )

        provider = ScriptedMock()
        outcome = VerificationLoop(provider, "mock-model", max_attempts=2).solve(
            "Compute 17 * 23 + 9; output only the integer.", lambda s: s.strip() == "400"
        )
        return _result(
            example=example_id,
            input_text=value,
            output=outcome.answer,
            elapsed=perf_counter() - start,
            attempts=outcome.attempts,
            trace=[
                {"step": "verify", "status": "rejected", "attempt": 1},
                {"step": "verify", "status": "accepted", "attempt": 2},
            ],
            validation={
                "status": "passed" if outcome.accepted else "failed",
                "check": "fixed_math_oracle",
                "expected": "400",
            },
            notes="Fixed synthetic math fixture; input text does not change the problem.",
        )
    raise AssertionError("Unreachable example")


COMPARISONS = (
    {
        "id": "retry_recovery",
        "title": "No retry versus bounded retry",
        "description": "Identical synthetic 429 then recovery sequence; neither branch uses the network.",
    },
    {
        "id": "prompt_construction",
        "title": "Direct versus template prompt",
        "description": "Identical topic; compare input transformation, not answer quality.",
    },
)


def compare(comparison_id: str, value: str) -> dict[str, Any]:
    if not isinstance(value, str) or not value.strip() or len(value) > 500:
        raise ValueError("Comparison input must contain 1–500 characters")
    if comparison_id == "retry_recovery":
        outcomes: list[dict[str, Any]] = []
        for strategy, tries in (("no_retry", 1), ("bounded_retry", 2)):
            provider = MockProvider(
                default_text="Recovered after transient error", faults=[RateLimitError("429")]
            )
            wrapped = ReliableProvider(
                provider,
                policy=RetryPolicy(
                    max_attempts=tries,
                    initial_delay_seconds=0,
                    jitter=False,
                ),
            )
            begin = perf_counter()
            try:
                reply = wrapped.generate(LLMRequest("mock-model", (Message("user", value),)))
                status, output = "completed", reply.text
            except Exception as error:
                from applied_ai.core.exceptions import LLMError

                if not isinstance(error, LLMError):
                    raise
                status, output = "error", error.category
            outcomes.append(
                {
                    "implementation": strategy,
                    "status": status,
                    "output": output,
                    "attempts": provider.call_count,
                    "latency_ms": round((perf_counter() - begin) * 1000, 3),
                    "cost_usd": None,
                }
            )
        return {
            "comparison": comparison_id,
            "input": value,
            "results": outcomes,
            "scope": "synthetic fixed 429; wall time is not provider latency",
        }
    if comparison_id == "prompt_construction":
        prompt = PromptTemplate("Explain {topic} for a beginner.").render({"topic": value.strip()})
        results = [
            {
                "implementation": "direct",
                "status": "completed",
                "output": value.strip(),
                "attempts": 0,
                "latency_ms": None,
                "cost_usd": None,
            },
            {
                "implementation": "template",
                "status": "completed",
                "output": prompt,
                "attempts": 0,
                "latency_ms": None,
                "cost_usd": None,
            },
        ]
        return {
            "comparison": comparison_id,
            "input": value,
            "results": results,
            "scope": "Prompt construction only; neither branch calls a model",
        }
    raise ValueError("Unknown comparison")
