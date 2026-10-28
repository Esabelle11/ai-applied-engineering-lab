# Bounded recovery loop graph

Use this pattern when output must be validated, retried a small number of
times, then escalated. The conditional edge makes the recovery policy visible
and prevents an unbounded self-correction loop.

```bash
uv run --offline --locked python engineering_patterns/09_langchain_and_langgraph/langgraph/recovery_loop/run.py
uv sync --extra agent-frameworks
uv run --extra agent-frameworks python engineering_patterns/09_langchain_and_langgraph/langgraph/recovery_loop/run.py --framework
```

Production retries also need timeouts, idempotency, provider-error handling,
and a persistent escalation queue.

