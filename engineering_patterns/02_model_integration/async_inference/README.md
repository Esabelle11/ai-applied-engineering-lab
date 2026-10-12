# Concurrent synchronous calls

## Problem and context
Illustrate a reusable model integration engineering capability without paid API calls. The example uses deterministic offline data and the shared `applied_ai` SDK.

## Mechanism and implementation
A bounded semaphore and asyncio.to_thread allow calls to an existing synchronous provider without blocking the event loop. Results retain input ordering.

## Run offline

```bash
uv run --locked python engineering_patterns/02_model_integration/async_inference/run.py
```

## Alternatives and tradeoffs
This is a threaded adapter, **not native async HTTP**; do not claim improved throughput without measuring. Real providers must be thread safe and must enforce timeouts. No streaming capability is claimed.

## Failure modes
Invalid configuration or unsupported capabilities raise exceptions. No hidden network calls, retries or quality guarantees are introduced in these demonstrations. Refer to the runnable tests for the negative paths.

## Validation and comparison
- Contract, success and failure tests: `tests/test_phase3_patterns.py`.
- No measured performance comparison is claimed. Phase 5 will introduce controlled benchmark reports.
- CLI example should run without credentials after project installation.

## Reuse
Uses canonical code in `src/applied_ai/` rather than maintaining duplicate implementation logic in the handbook.
