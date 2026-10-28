# LangChain & LangGraph

This category groups framework-specific patterns by their primary abstraction.
The examples are independent of the core `applied_ai` SDK: they show where a
framework is useful without making it a project-wide runtime dependency.

```text
09_langchain_and_langgraph/
├── langchain/  # model, tools, retrieval, and compact agent loops
└── langgraph/  # explicit state, routing, review gates, and recovery graphs
```

Each default command is a deterministic replay. To execute the matching
framework objects locally, install the optional extra and pass `--framework`:

```bash
uv sync --extra agent-frameworks
uv run --extra agent-frameworks python \
  engineering_patterns/09_langchain_and_langgraph/langgraph/specialist_routing/run.py \
  --framework
```

Neither mode calls a hosted model. Add model access only with explicit tool
permissions, output validation, tracing, and an approval boundary.

