# Bounded policy tool assistant

Use this when an assistant needs one approved lookup before drafting a helpdesk
reply. The tool is local and read-only; a hosted model is deliberately absent.

```bash
uv run --offline --locked python engineering_patterns/09_langchain_and_langgraph/langchain/simple_tool_assistant/run.py
uv sync --extra agent-frameworks
uv run --extra agent-frameworks python engineering_patterns/09_langchain_and_langgraph/langchain/simple_tool_assistant/run.py --framework
```

The framework path declares a LangChain `@tool` and composes its output with a
`RunnableLambda`. In production, allowlist tools and validate drafts before
sending them to a customer.

