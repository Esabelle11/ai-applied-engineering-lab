# Single agent

Runs one named agent against an immutable input-state snapshot and returns a fresh state with its updates.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/03_agent_orchestration/single_agent/run.py
```

This is a deterministic, offline implementation. Production workflows should add durable storage, idempotency, authorization, and observability around any external side effects.
