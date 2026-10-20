# Output Validation

Rejects empty or out-of-policy text output before it reaches the next workflow step.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/05_reliability_engineering/output_validation/run.py
```

The example is deterministic and local. Production use needs durable coordination, metrics, and policies appropriate to its external side effects.
