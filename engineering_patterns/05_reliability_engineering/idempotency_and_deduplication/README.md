# Idempotency And Deduplication

Caches successful work under a caller-owned key to prevent duplicate in-process side effects.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/05_reliability_engineering/idempotency_and_deduplication/run.py
```

The example is deterministic and local. Production use needs durable coordination, metrics, and policies appropriate to its external side effects.
