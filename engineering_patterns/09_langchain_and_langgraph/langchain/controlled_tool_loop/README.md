# Controlled calculator tool loop

Use this when a workflow has a fixed, reviewable plan of safe tool calls. The
example runs two calculator calls and summarizes them; it never permits an
unbounded model-directed loop.

```bash
uv run --offline --locked python engineering_patterns/09_langchain_and_langgraph/langchain/controlled_tool_loop/run.py
uv sync --extra agent-frameworks
uv run --extra agent-frameworks python engineering_patterns/09_langchain_and_langgraph/langchain/controlled_tool_loop/run.py --framework
```

Set maximum iterations, validate arguments, and use idempotency controls before
adapting a tool loop to side-effecting operations.

