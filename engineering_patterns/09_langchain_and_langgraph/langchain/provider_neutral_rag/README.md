# Provider-neutral local RAG

Use this pattern to retrieve a small approved corpus and preserve evidence IDs
with the answer. It uses LangChain documents and runnables, but no embedding
provider or hosted model.

```bash
uv run --offline --locked python engineering_patterns/09_langchain_and_langgraph/langchain/provider_neutral_rag/run.py
uv sync --extra agent-frameworks
uv run --extra agent-frameworks python engineering_patterns/09_langchain_and_langgraph/langchain/provider_neutral_rag/run.py --framework
```

For production, add a tested retrieval index, citation checks, and access
control before introducing model-generated prose.

