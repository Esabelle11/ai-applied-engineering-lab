# Phase 1 — Core LLM Interface (D1)

This milestone follows the architecture in [`PROJECT_ARCHITECTURE_AND_ROADMAP.md`](PROJECT_ARCHITECTURE_AND_ROADMAP.md).

## Implemented
- Immutable request/response/message models with explicit validation.
- Synchronous provider protocol and capability metadata.
- Deterministic mock backend with scripted faults and keyed prompts.
- OpenAI Responses API backend, HTTP mock injection, locally measured latency.
- JSON schema-based structured output, with explicit capability checks.
- Normalized categorized exceptions; no SDK-level retry behavior in Phase 1.
- Runnable pattern and offline HTTP/contract tests; optional live smoke test.

## Local checks
```bash
uv lock
uv sync --locked --group dev --extra openai
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy src
uv run --locked pytest -q
uv run --locked python scripts/validate_patterns.py
uv run --locked python engineering_patterns/02_model_integration/basic_api_integration/run.py
```

## Phase 1 boundaries
- Text messages only. No streaming/async, tools, model registry, fallback, or retries.
- API schema conformity can vary by model. Backend 400s are normalized.
- The OpenAI adapter requires `httpx` from the optional `openai` extra.
- JSON schema validation uses the `jsonschema` dependency.
- Structured outputs must be JSON objects; refusal is an exception.
- Request-level timeouts exist; overall retry deadline belongs to Phase 2.

## Exit gate
- [x] Offline example returns a deterministic result in development tests.
- [x] Offline provider and HTTP contract tests are included.
- [x] Unsupported capability paths are tested to fail explicitly.
- [x] Errors are normalized into documented types and tested.
- [ ] Real API smoke test is run by contributor explicitly with credentials.
- [ ] GitHub Actions checked in the user's repo.
