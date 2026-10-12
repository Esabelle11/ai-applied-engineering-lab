# Request-keyed response caching

## Problem and context
Illustrate a reusable optimization engineering capability without paid API calls. The example uses deterministic offline data and the shared `applied_ai` SDK.

## Mechanism and implementation
The opt-in cache hashes all content and generation settings into an in-memory key. TTL expiration and per-instance isolation are supported.

## Run offline

```bash
uv run --locked python engineering_patterns/07_optimization/response_caching/run.py
```

## Alternatives and tradeoffs
Caching can return stale or unwanted answers. It is process-local and not thread safe; no live-provider performance claims are made. Do not share one instance between unrelated tenants or cache sensitive outputs by default.

## Failure modes
Invalid configuration or unsupported capabilities raise exceptions. No hidden network calls, retries or quality guarantees are introduced in these demonstrations. Refer to the runnable tests for the negative paths.

## Validation and comparison
- Contract, success and failure tests: `tests/test_phase3_patterns.py`.
- No measured performance comparison is claimed. Phase 5 will introduce controlled benchmark reports.
- CLI example should run without credentials after project installation.

## Reuse
Uses canonical code in `src/applied_ai/` rather than maintaining duplicate implementation logic in the handbook.
