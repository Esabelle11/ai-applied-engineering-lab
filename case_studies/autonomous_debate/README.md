# Autonomous Debate — State Graph Reference

**Problem:** Coordinating multiple agent roles requires explicit transitions and state lifecycles.

**Architecture:** provider-neutral `LLMProvider` (02) → `GraphNode` speaker roles (03) → `StateGraph` (03) → `GraphSnapshot` checkpoint/resume (03).

Workflow: `opening → optimist → skeptic → synthesis → END`.

```sh
uv run python -m case_studies.autonomous_debate.run
uv run python -m case_studies.autonomous_debate.run --live  # opt-in
```

The demonstration runs two steps, records a snapshot, then resumes for two more steps. This is **in-memory checkpointing**, not durable crash recovery or LangGraph parity.

**Tests:** `tests/test_phase4_cases.py::test_graph_completes_and_resumes`.

**Limitations:** Model-generated arguments are not guaranteed to be true or diverse. No parallelism, durable persistence, knowledge graph, moderation, or external effects.
