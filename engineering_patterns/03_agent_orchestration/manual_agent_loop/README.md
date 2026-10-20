# Manual agent loop

Runs a caller-controlled decision loop with a fixed step budget and an explicit completed result.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/03_agent_orchestration/manual_agent_loop/run.py
```

This is a deterministic, offline implementation. Production workflows should add durable storage, idempotency, authorization, and observability around any external side effects.
