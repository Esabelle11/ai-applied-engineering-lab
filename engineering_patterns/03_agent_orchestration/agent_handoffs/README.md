# Agent handoffs

Runs a small two-agent handoff: the triage agent creates a transfer containing the question and reason, a dispatcher looks up the destination agent, and the billing specialist receives that transferred state and produces the final response.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/03_agent_orchestration/agent_handoffs/run.py
```
Advance: 
```bash
uv run --offline --locked python engineering_patterns/03_agent_orchestration/agent_handoffs/run_advance.py
```

This is a deterministic, offline implementation. The agent registry and dispatcher are deliberately explicit so the execution effect is visible. Production workflows should add durable storage, idempotency, authorization, and observability around any external side effects.
