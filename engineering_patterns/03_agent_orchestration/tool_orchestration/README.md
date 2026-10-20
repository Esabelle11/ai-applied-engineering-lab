# Tool orchestration

Uses an explicitly registered tool boundary; unregistered tools cannot be invoked.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/03_agent_orchestration/tool_orchestration/run.py
```

This is a deterministic, offline implementation. Production workflows should add durable storage, idempotency, authorization, and observability around any external side effects.
