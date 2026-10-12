# Retry backoff policy comparison

## Problem and context
Illustrate a reusable reliability engineering engineering capability without paid API calls. The example uses deterministic offline data and the shared `applied_ai` SDK.

## Mechanism and implementation
Compare fixed versus exponential waiting schedules using the same synthetic error and bounded policy settings. It reuses the canonical Phase 2 RetryPolicy implementation.

## Run offline

```bash
uv run --locked python engineering_patterns/05_reliability_engineering/exponential_backoff/run.py
```

## Alternatives and tradeoffs
These are **analytical delays**, not latency measurements or live success rates. Jitter and server Retry-After can change actual waits. Increasing retries can increase cost and latency.

## Failure modes
Invalid configuration or unsupported capabilities raise exceptions. No hidden network calls, retries or quality guarantees are introduced in these demonstrations. Refer to the runnable tests for the negative paths.

## Validation and comparison
- Contract, success and failure tests: `tests/test_phase3_patterns.py`.
- No measured performance comparison is claimed. Phase 5 will introduce controlled benchmark reports.
- CLI example should run without credentials after project installation.

## Reuse
Uses canonical code in `src/applied_ai/` rather than maintaining duplicate implementation logic in the handbook.
