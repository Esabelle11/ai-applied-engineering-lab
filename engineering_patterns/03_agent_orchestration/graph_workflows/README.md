# Stateful graph and checkpoint resume

## Problem and context
Illustrate a reusable agent orchestration engineering capability without paid API calls. The example uses deterministic offline data and the shared `applied_ai` SDK.

## Mechanism and implementation
A deterministic manual state graph uses explicit nodes, bounded steps, immutable snapshots and continuation from a checkpoint. No LangGraph dependency is required.

## Run offline

```bash
uv run --locked python engineering_patterns/03_agent_orchestration/graph_workflows/run.py
```

## Alternatives and tradeoffs
Snapshots are in memory, not durable after process termination. Resuming a graph may repeat external side effects without idempotency controls. Bounded max_steps does not guarantee termination of a node callback.

## Failure modes
Invalid configuration or unsupported capabilities raise exceptions. No hidden network calls, retries or quality guarantees are introduced in these demonstrations. Refer to the runnable tests for the negative paths.

## Validation and comparison
- Contract, success and failure tests: `tests/test_patterns.py`.
- No measured performance comparison is claimed.
- CLI example should run without credentials after project installation.

## Reuse
Uses canonical code in `src/applied_ai/` rather than maintaining duplicate implementation logic in the handbook.
