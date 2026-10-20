# Planner executor

Separates a declared plan from deterministic execution, preserving the state produced by each plan step.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/03_agent_orchestration/planner_executor/run.py
```

This is a deterministic, offline implementation. Production workflows should add durable storage, idempotency, authorization, and observability around any external side effects.
