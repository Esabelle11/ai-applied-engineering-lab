# WhyBuddy — Multi-Model Reference

**Problem:** Applications need explicit policies to route simple questions and detailed requests without rewriting provider-specific application code.

**Architecture:** `.env` configuration → `ProviderFactory` (02) → `TaskRouter` + `ModelTarget` (02) → normalized `LLMResponse` (02). The SDK owns routing; the case study chooses task names and prompts.

```sh
uv run python -m case_studies.whybuddy.run
# Live: select credentials/provider/model in .env
uv run python -m case_studies.whybuddy.run --live
```

Set `AI_LAB_FAST_MODEL` and `AI_LAB_DETAILED_MODEL` to different supported model IDs on **the same selected provider**. Cross-provider task routing can be composed later by configuring separate SDK `ModelTarget` instances.

**Tests:** `tests/test_phase4_cases.py::test_whybuddy_uses_task_router`.

**Limitations:** Named-task routing, not AI-based query classification. Models may have different prices and feature support. No automatic best-model claims.
