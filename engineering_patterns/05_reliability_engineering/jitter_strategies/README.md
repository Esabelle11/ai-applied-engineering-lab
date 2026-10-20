# Jitter Strategies

Calculates bounded full jitter from an explicit deterministic random fraction.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/05_reliability_engineering/jitter_strategies/run.py
```

The example is deterministic and local. Production use needs durable coordination, metrics, and policies appropriate to its external side effects.
