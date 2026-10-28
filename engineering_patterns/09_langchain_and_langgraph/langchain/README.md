# LangChain patterns

Use LangChain where composable tools, documents, and runnables make a compact
agentic flow clearer. Move to LangGraph if the work grows durable state,
branching, or human review requirements.

| Pattern | Suitable task |
| --- | --- |
| `simple_tool_assistant` | Search an approved policy source and draft a response. |
| `provider_neutral_rag` | Retrieve local evidence and compose a cited answer. |
| `controlled_tool_loop` | Execute a bounded plan of approved tools, then summarize. |

