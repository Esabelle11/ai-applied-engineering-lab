# Long-running case workflow graph

Use this when a case proceeds through intake, research, review, and follow-up,
and state must remain understandable at every stage. The replay shows the state
shape and stage history without requiring a persistent store.

```bash
uv run --offline --locked python engineering_patterns/09_langchain_and_langgraph/langgraph/long_running_case/run.py
uv sync --extra agent-frameworks
uv run --extra agent-frameworks python engineering_patterns/09_langchain_and_langgraph/langgraph/long_running_case/run.py --framework
```

Use a LangGraph checkpointer and an application-owned case store before making
the workflow durable. Keep external communication in a reviewed final step.

