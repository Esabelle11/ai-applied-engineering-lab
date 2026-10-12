# Prompt Forge — Mini Reference Application

**Problem:** Templates tend to be tested subjectively. This example renders two variants of a capital-city answer prompt and evaluates both with an exact-match metric over two synthetic questions.

**Architecture:** `PromptTemplate` (01) → provider-neutral `LLMRequest` (02) → `evaluate` / `exact_match` (06) → score report. The SDK owns templating and evaluation; this case study owns only the two toy prompts and the synthetic dataset.

```sh
uv run python -m case_studies.prompt_forge.run
# Optional: set AI_LAB_PROVIDER, AI_LAB_MODEL and key in .env, then
uv run python -m case_studies.prompt_forge.run --live
```

**Tests:** `tests/test_phase4_cases.py::test_prompt_forge_evaluates_two_templates`.

**Limitations:** Only two cases; exact-match is *not* semantic quality. Offline mocks validate wiring, not real-model accuracy. Live outputs may be nondeterministic and the example issues four calls. Don't infer that one prompt is universally better.
