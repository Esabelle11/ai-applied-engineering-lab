# State management

Demonstrates that orchestration transitions produce a new state snapshot without mutating the prior state.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/03_agent_orchestration/state_management/run.py
```

This is a deterministic, offline implementation. Production workflows should add durable storage, idempotency, authorization, and observability around any external side effects.
