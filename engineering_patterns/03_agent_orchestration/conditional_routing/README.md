# Conditional routing

Selects exactly one branch from explicit state predicates, failing closed for zero or multiple matches.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/03_agent_orchestration/conditional_routing/run.py
```

This is a deterministic, offline implementation. Production workflows should add durable storage, idempotency, authorization, and observability around any external side effects.
