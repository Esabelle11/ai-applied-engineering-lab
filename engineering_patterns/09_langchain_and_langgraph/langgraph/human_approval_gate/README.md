# Human approval gate graph

Use this when a generated draft must stop at a review boundary before any
consequential action. The graph emits `AWAITING_HUMAN_REVIEW` unless an
application provides a reviewer decision.

```bash
uv run --offline --locked python engineering_patterns/09_langchain_and_langgraph/langgraph/human_approval_gate/run.py
uv sync --extra agent-frameworks
uv run --extra agent-frameworks python engineering_patterns/09_langchain_and_langgraph/langgraph/human_approval_gate/run.py --framework
```

The approval value is synthetic. A real implementation needs authenticated
reviewers, persistent state, audit logging, and a separate submission boundary.

