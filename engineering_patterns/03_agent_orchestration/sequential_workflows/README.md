# Sequential workflows

Executes dependent agents in declared order, passing each update to the next step.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/03_agent_orchestration/sequential_workflows/run.py
```

This is a deterministic, offline implementation. Production workflows should add durable storage, idempotency, authorization, and observability around any external side effects.
