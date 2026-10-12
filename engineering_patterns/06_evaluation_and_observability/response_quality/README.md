# Deterministic evaluation dataset

## Problem and context
Illustrate a reusable evaluation and observability engineering capability without paid API calls. The example uses deterministic offline data and the shared `applied_ai` SDK.

## Mechanism and implementation
Compare predictions to a small labeled dataset using deterministic case/whitespace-normalized exact match. Report the numerator and denominator alongside accuracy.

## Run offline

```bash
uv run --locked python engineering_patterns/06_evaluation_and_observability/response_quality/run.py
```

## Alternatives and tradeoffs
The dataset is synthetic and tiny. Exact match does not measure semantic correctness or actual model quality. Benchmark conclusions require representative datasets and uncertainty analysis.

## Failure modes
Invalid configuration or unsupported capabilities raise exceptions. No hidden network calls, retries or quality guarantees are introduced in these demonstrations. Refer to the runnable tests for the negative paths.

## Validation and comparison
- Contract, success and failure tests: `tests/test_phase3_patterns.py`.
- No measured performance comparison is claimed. Phase 5 will introduce controlled benchmark reports.
- CLI example should run without credentials after project installation.

## Reuse
Uses canonical code in `src/applied_ai/` rather than maintaining duplicate implementation logic in the handbook.
