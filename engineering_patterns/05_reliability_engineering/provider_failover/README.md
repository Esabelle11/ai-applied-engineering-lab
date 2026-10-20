# Provider Failover

Moves from a uniquely named failed provider to an explicitly configured fallback provider.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/05_reliability_engineering/provider_failover/run.py
```

The example is deterministic and local. Production use needs durable coordination, metrics, and policies appropriate to its external side effects.
