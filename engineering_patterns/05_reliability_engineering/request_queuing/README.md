# Request Queuing

Provides a bounded in-memory FIFO queue that the caller drains explicitly.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/05_reliability_engineering/request_queuing/run.py
```

The example is deterministic and local. Production use needs durable coordination, metrics, and policies appropriate to its external side effects.
