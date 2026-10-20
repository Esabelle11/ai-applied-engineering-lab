# Rate Limiting

Applies a process-local token bucket before a request is admitted.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/05_reliability_engineering/rate_limiting/run.py
```

The example is deterministic and local. Production use needs durable coordination, metrics, and policies appropriate to its external side effects.
