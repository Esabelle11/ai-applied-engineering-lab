# Explicit capability detection

## Problem and context
Illustrate a reusable model integration engineering capability without paid API calls. The example uses deterministic offline data and the shared `applied_ai` SDK.

## Mechanism and implementation
Check provider advertised capabilities before requesting schema-enforced output; fail rather than silently reducing correctness guarantees.

## Run offline

```bash
uv run --locked python engineering_patterns/02_model_integration/model_capability_detection/run.py
```

## Alternatives and tradeoffs
A provider-level capability flag does not guarantee every model or schema is supported. Actual model compatibility may only be established by an API error.

## Failure modes
Invalid configuration or unsupported capabilities raise exceptions. No hidden network calls, retries or quality guarantees are introduced in these demonstrations. Refer to the runnable tests for the negative paths.

## Validation and comparison
- Contract, success and failure tests: `tests/test_patterns.py`.
- No measured performance comparison is claimed.
- CLI example should run without credentials after project installation.

## Reuse
Uses canonical code in `src/applied_ai/` rather than maintaining duplicate implementation logic in the handbook.
