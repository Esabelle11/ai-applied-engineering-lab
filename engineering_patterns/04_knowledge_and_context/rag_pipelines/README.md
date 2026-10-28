# Offline lexical retrieval and grounded prompt

## Problem and context
Illustrate a reusable knowledge and context engineering capability without paid API calls. The example uses deterministic offline data and the shared `applied_ai` SDK.

## Mechanism and implementation
Token-overlap retrieval selects locally stored source documents, then passes them to the same common LLM provider interface. It records retrieved document IDs separately from generated text.

## Run offline

```bash
uv run --locked python engineering_patterns/04_knowledge_and_context/rag_pipelines/run.py
```

## Alternatives and tradeoffs
This is **lexical retrieval**, not embeddings or production RAG. Retrieved documents are untrusted. A cited response is not necessarily faithful; source agreement is not independently verified. No-result questions are rejected.

## Failure modes
Invalid configuration or unsupported capabilities raise exceptions. No hidden network calls, retries or quality guarantees are introduced in these demonstrations. Refer to the runnable tests for the negative paths.

## Validation and comparison
- Contract, success and failure tests: `tests/test_patterns.py`.
- No measured performance comparison is claimed.
- CLI example should run without credentials after project installation.

## Reuse
Uses canonical code in `src/applied_ai/` rather than maintaining duplicate implementation logic in the handbook.
