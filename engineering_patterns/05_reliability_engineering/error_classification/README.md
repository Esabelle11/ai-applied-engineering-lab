# Error Classification

Classifies normalized exceptions into explicit categories and retryability decisions.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/05_reliability_engineering/error_classification/run.py
```

The example is deterministic and local. Production use needs durable coordination, metrics, and policies appropriate to its external side effects.
