# Failure Recovery

Uses the shared reliable-provider wrapper to retry a bounded transient provider failure.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/05_reliability_engineering/failure_recovery/run.py
```

The example is deterministic and local. Production use needs durable coordination, metrics, and policies appropriate to its external side effects.
