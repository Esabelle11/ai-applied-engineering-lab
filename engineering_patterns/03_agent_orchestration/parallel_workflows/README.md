# Parallel workflows

Runs independent agents with bounded concurrency and merges only non-conflicting outputs.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/03_agent_orchestration/parallel_workflows/run.py
```

This is a deterministic, offline implementation. Production workflows should add durable storage, idempotency, authorization, and observability around any external side effects.
