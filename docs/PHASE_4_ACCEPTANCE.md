# Phase 4 — D4 Acceptance Report

**Target:** Five small, clear SDK-consuming reference applications with tests, architecture maps, and synthetic fixtures.

| Requirement | Evidence |
|---|---|
| Simplified Prompt Forge | `case_studies/prompt_forge/` |
| Simplified WhyBuddy | `case_studies/whybuddy/` |
| Simplified Autonomous Debate | `case_studies/autonomous_debate/` |
| Simplified CitizenAssist | `case_studies/citizen_assist/` |
| Simplified Math Reasoning | `case_studies/math_reasoning/` |
| Shared SDK | `src/applied_ai/` for prompts, routing, graph, retrieval, reasoning, execution and providers |
| Architecture maps | `docs/PHASE_4_ARCHITECTURE_MAPS.md` |
| Opt-in switchable providers | `src/applied_ai/providers/factory.py`, `.env.example` |
| Deterministic offline tests | `tests/test_phase4_cases.py`, `tests/test_phase4_providers.py` |

## Required local verification

```sh
uv lock
uv sync --locked --group dev --extra providers
uv run --locked pytest -q
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy src
uv run --locked python scripts/validate_patterns.py
uv run --offline --locked python scripts/run_all_patterns.py
uv run --offline --locked python scripts/run_all_case_studies.py
```

**D4 limitations:** Live provider interoperability, real Docker execution, GitHub Actions, Ruff, and mypy must be checked in the contributor environment if not available in the packaging environment. The provider REST adapters were tested using mocked HTTP; that does **not** prove current live account/model compatibility. OpenRouter may change free-tier limits. Math execution is opt-in Docker, not run on the host or required for offline acceptance; the sandbox is not considered production-hardened.
