# Structured Output Recovery

Decodes JSON and verifies required keys without unsafe repair or execution.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/05_reliability_engineering/structured_output_recovery/run.py
```

The example is deterministic and local. Production use needs durable coordination, metrics, and policies appropriate to its external side effects.
