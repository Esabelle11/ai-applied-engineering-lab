# Multi-agent

Composes a researcher and reviewer through explicit state passing, so ownership and dependencies remain visible.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/03_agent_orchestration/multi_agent/run.py
```

This is a deterministic, offline implementation. Production workflows should add durable storage, idempotency, authorization, and observability around any external side effects.
