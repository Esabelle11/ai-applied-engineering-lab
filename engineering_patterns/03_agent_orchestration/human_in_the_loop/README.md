# Human in the loop

Requires a recorded approve/reject decision before a sensitive action can proceed.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/03_agent_orchestration/human_in_the_loop/run.py
```

This is a deterministic, offline implementation. Production workflows should add durable storage, idempotency, authorization, and observability around any external side effects.
