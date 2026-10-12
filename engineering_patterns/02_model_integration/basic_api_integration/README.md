# Basic API Integration — Provider-neutral generation

## Problem
A demonstration should not need to rewrite its prompt or response-processing code
when switching from an offline fake model to a live provider.

## Mechanism
Both adapters implement `LLMProvider.generate(LLMRequest) -> LLMResponse`.
The SDK normalizes token usage, request ID, provider name, and latency when available.

## Run (offline)

```bash
uv run --locked python engineering_patterns/02_model_integration/basic_api_integration/run.py
```

Expected response: `RAG grounds a model's answer in retrieved documents.`

## Run (live; opt-in and may incur API charges)

```bash
export OPENAI_API_KEY="YOUR_KEY"  # configure locally, NEVER commit this value
uv run --locked python engineering_patterns/02_model_integration/basic_api_integration/run.py --provider openai --model gpt-4.1-mini
```

The live adapter uses the OpenAI **Responses API** (`POST /v1/responses`)
with `store=false`. It needs the optional `openai` project extra (`httpx`).
No `.env` is automatically loaded.

## Variations
Use `StructuredOutputSpec` for a JSON schema, supported only by capable providers/models.
Unsupported capabilities raise `CapabilityNotSupportedError` instead of downgrading silently.
SDK-level retries, streaming, async generation, and tools are not part of Phase 1.

## Validation & limits
- Tests: `tests/test_provider_contract.py`, `tests/test_openai_http.py`.
- Offline HTTP tests use `httpx.MockTransport`; they never make API calls.
- The live smoke test is opt-in and requires a separate environment flag.
- An OpenAI model may reject unsupported sampling/schema options even when the
  provider supports them in general; an HTTP 400 becomes `InvalidRequestError`.
- Backend usage may be unavailable; do not estimate token counts as if observed.
- Latency measures client-side wall time, not model-internal generation time.

## Reuse
Import `applied_ai.LLMRequest`, `applied_ai.Message`, and `applied_ai.MockProvider`,
or `applied_ai.providers.openai_provider.OpenAIProvider` for the live implementation.
