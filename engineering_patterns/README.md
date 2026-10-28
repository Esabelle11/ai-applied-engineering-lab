# Engineering Patterns Handbook

This directory is the primary educational product. **The numbered categories
are independent topics, not consecutive runtime pipeline stages.** A real
application may combine any subset of patterns.

## Categories

| ID | Topic |
| --- | --- |
| 01_prompt_engineering | [Prompt Engineering](01_prompt_engineering/README.md) |
| 02_model_integration | [Model Integration](02_model_integration/README.md) |
| 03_agent_orchestration | [Agent Orchestration](03_agent_orchestration/README.md) |
| 04_knowledge_and_context | [Knowledge & Context](04_knowledge_and_context/README.md) |
| 05_reliability_engineering | [Reliability Engineering](05_reliability_engineering/README.md) |
| 06_evaluation_and_observability | [Evaluation & Observability](06_evaluation_and_observability/README.md) |
| 07_optimization | [Optimization](07_optimization/README.md) |
| 08_reasoning_and_execution | [Reasoning & Execution](08_reasoning_and_execution/README.md) |
| 09_langchain_and_langgraph | [LangChain & LangGraph](09_langchain_and_langgraph/README.md) |

## Pattern contract

1. Each concrete pattern lives in a directory below exactly one category. A category may use grouping folders when they make a framework distinction clear.
2. Include `README.md`, `pattern.yaml`, and a runnable `run.py`.
3. Implement or import reusable utilities from `src/applied_ai` when appropriate.
4. Provide deterministic no-key/no-network examples whenever possible.
5. Explain prerequisites, tradeoffs, failure modes, and how to test.
6. Reference related patterns instead of duplicating their implementations.

See [`_template/`](_template/) for the starter layout.

## Executing the catalog

Run any `run.py` by its relative path or run all published offline demonstrations:

```bash
uv run --offline --locked python scripts/run_all_patterns.py
```

See [the full pattern catalog](../docs/PATTERN_CATALOG.md) for current examples.
