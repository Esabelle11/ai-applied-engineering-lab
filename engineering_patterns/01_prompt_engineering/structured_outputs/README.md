# Schema-constrained generation

## Problem and context
Illustrate a reusable prompt engineering engineering capability without paid API calls. The example uses deterministic offline data and the shared `applied_ai` SDK.

## Mechanism and implementation
Reuse shared JSON Schema contracts and the local validator. The mock example provides deterministic schema-valid data.

## Run offline

```bash
uv run --locked python engineering_patterns/01_prompt_engineering/structured_outputs/run.py
```

## Alternatives and tradeoffs
Schema validity is not factual correctness. API-side strict schema support differs by provider/model, and local validation is still required.

## Failure modes
Invalid configuration or unsupported capabilities raise exceptions. No hidden network calls, retries or quality guarantees are introduced in these demonstrations. Refer to the runnable tests for the negative paths.

## Validation and comparison
- Contract, success and failure tests: `tests/test_patterns.py`.
- No measured performance comparison is claimed.
- CLI example should run without credentials after project installation.

## Reuse
Uses canonical code in `src/applied_ai/` rather than maintaining duplicate implementation logic in the handbook.
