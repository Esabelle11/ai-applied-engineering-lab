# Agent failure recovery

Retries only caller-selected exception types within a bounded attempt budget and records prior error types.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/03_agent_orchestration/agent_failure_recovery/run.py
```

This is a deterministic, offline implementation. Production workflows should add durable storage, idempotency, authorization, and observability around any external side effects.
