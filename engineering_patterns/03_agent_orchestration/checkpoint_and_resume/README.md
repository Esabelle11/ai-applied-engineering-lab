# Checkpoint and resume

Stores an immutable in-memory checkpoint under a caller-provided ID and resumes from a copy.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/03_agent_orchestration/checkpoint_and_resume/run.py
```

This is a deterministic, offline implementation. Production workflows should add durable storage, idempotency, authorization, and observability around any external side effects.
