# Circuit Breakers

Tracks transient failures and opens a circuit to reject calls during a configured recovery window.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/05_reliability_engineering/circuit_breakers/run.py
```

The example is deterministic and local. Production use needs durable coordination, metrics, and policies appropriate to its external side effects.
