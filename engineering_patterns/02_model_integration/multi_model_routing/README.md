# Task-based model routing

## Problem and context
Illustrate a reusable model integration engineering capability without paid API calls. The example uses deterministic offline data and the shared `applied_ai` SDK.

## Mechanism and implementation
Explicit routes assign a provider and its model ID to each task. The common request is copied with the selected model; no inference capability is invented. Unknown tasks fail closed.

## Run offline

```bash
uv run --locked python engineering_patterns/02_model_integration/multi_model_routing/run.py
```

## Alternatives and tradeoffs
Route choice is caller-defined, not an automatic quality or cost optimizer. Providers can have differing capabilities. The router rejects unsupported structured output instead of silently falling back.

## Failure modes
Invalid configuration or unsupported capabilities raise exceptions. No hidden network calls, retries or quality guarantees are introduced in these demonstrations. Refer to the runnable tests for the negative paths.

## Validation and comparison
- Contract, success and failure tests: `tests/test_phase3_patterns.py`.
- No measured performance comparison is claimed. Phase 5 will introduce controlled benchmark reports.
- CLI example should run without credentials after project installation.

## Reuse
Uses canonical code in `src/applied_ai/` rather than maintaining duplicate implementation logic in the handbook.
