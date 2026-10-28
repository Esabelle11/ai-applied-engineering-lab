# Specialist routing graph

Use this when each intake should reach one of a small number of approved
specialist queues. The classification function is deterministic here; replace
it only with a validated classifier and a clear fallback policy.

```bash
uv run --offline --locked python engineering_patterns/09_langchain_and_langgraph/langgraph/specialist_routing/run.py
uv sync --extra agent-frameworks
uv run --extra agent-frameworks python engineering_patterns/09_langchain_and_langgraph/langgraph/specialist_routing/run.py --framework
```

The graph sends only a queue recommendation. It performs no external handoff.

