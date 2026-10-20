# Timeout Handling

Passes a total request deadline through the existing reliable-provider wrapper.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/05_reliability_engineering/timeout_handling/run.py
```

The example is deterministic and local. Production use needs durable coordination, metrics, and policies appropriate to its external side effects.
