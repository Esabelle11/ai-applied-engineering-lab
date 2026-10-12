# Phase 3 — Engineering-Pattern Library (D3)

## Status and scope

This release extends the Phase 2 codebase with **11 new self-contained executable patterns** distributed across **all eight independent handbook categories**. Together with the existing three patterns, 14 runnable patterns are published. This is a curated milestone, **not** implementation of every subdirectory listed in the long-term roadmap.

The `engineering_patterns/` directory owns examples and documentation. `src/applied_ai/` owns reusable code. No SDK module imports from the handbook.

## Implemented SDK capabilities

| SDK module | Role |
|---|---|
| `applied_ai.routing` | Explicit task → provider/model routing with schema capability checks |
| `applied_ai.inference` | Bounded thread-backed concurrent execution over sync provider contracts |
| `applied_ai.prompting` | Safe simple-field templating and sequential prompt chaining |
| `applied_ai.orchestration` | Deterministic in-memory state graph and checkpoint continuation |
| `applied_ai.knowledge` | Offline lexical search + source-aware prompt composition |
| `applied_ai.reasoning` | Bounded propose–verify loop with supplied independent verifier |
| `applied_ai.evaluation` | Case/whitespace-normalized exact-match dataset evaluation |
| `applied_ai.optimization` | Explicit TTL-backed in-process response caching |

Phase 1 `StructuredOutputSpec` and Phase 2 `RetryPolicy` are reused by new patterns.

## Published patterns

- Prompt Engineering: `prompt_templates`, `prompt_chaining`, `structured_outputs`.
- Model Integration: `basic_api_integration`, `multi_model_routing`, `async_inference`, `model_capability_detection`.
- Reliability: `retry_mechanisms`, `exponential_backoff`.
- Agent Orchestration: `graph_workflows`.
- Knowledge & Context: `rag_pipelines` (lexical, not embedding-based).
- Reasoning & Execution: `plan_execute_verify` (no arbitrary code execution).
- Evaluation & Observability: `response_quality` (exact match, not LLM-as-judge).
- Optimization: `response_caching` (local cache, not distributed).

## Acceptance and local validation

```bash
uv lock
uv sync --locked --group dev --extra openai
uv run --locked python scripts/validate_patterns.py
uv run --offline --locked python scripts/run_all_patterns.py
uv run --offline --locked pytest -q
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy src
uv run --locked python scripts/check_no_secrets.py
uv build
```

The 11 new patterns each have documentation, a manifest, an offline `run.py`, and successful and failure-oriented tests in `tests/test_phase3_patterns.py`. The existing optional live smoke test is skipped by default.

## Significant limitations and future work

- **Streaming:** no partial-token streaming transport is implemented yet. Do not simulate streaming by splitting completed text. Add an explicit stream protocol and actual provider SSE handling in a later increment.
- **Native async:** current concurrent adapter uses threads and the synchronous provider interface; it is not native asynchronous HTTP. Cancellation of a waiting coroutine may not stop in-flight synchronous work.
- **Provider parity:** live OpenAI remains the only integrated cloud backend; mock providers demonstrate routing but not interoperability with another live provider.
- **RAG:** lexical overlap is a small illustrative retrieval algorithm. Vector search, reranking, semantic embeddings, retrieval evaluation, and adversarial document handling are future tasks. Source IDs describe retrieved documents; citations do not guarantee truthfulness.
- **Graph:** callbacks execute synchronously and graph checkpoints reside in memory. Production resumability needs persistent checkpoints, replay rules and side-effect idempotency.
- **Reasoning:** the verifier is supplied by the caller. No generated Python is executed, and no security sandbox is implied.
- **Caching:** local opt-in TTL cache is not cross-process, thread-safe, or appropriate to share across tenants. Cache returns the original response object including its original latency; `CacheResult.hit` distinguishes reuse.
- **Evaluation:** synthetic data and exact match do not establish field performance. Phase 5 adds representative datasets, run metadata, and uncertainty analysis.
- **Benchmarking:** the simple backoff comparison is deterministic schedule arithmetic, **not measured response performance**.

## Dependency and release note

The Phase 3 distribution is based on the previously delivered Phase 2 ZIP, not your local working tree. The **update ZIP deliberately omits existing Phase 2 source files**, so local style fixes are preserved. Regenerate and commit a genuine `uv.lock` on a machine with package registry access after copying updates. Check CI after pushing; no CI run can be claimed from local testing alone.
