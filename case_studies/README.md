# Phase 4 — Five SDK-based case studies

These are *small synthetic reference implementations*, **not** copies of the original products. Their components import `applied_ai` from `src/` and compose previously tested engineering patterns. By default **no API calls** occur.

| Study | Demonstrates | Offline command |
|---|---|---|
| Prompt Forge | Prompt templates + evaluation | `uv run python -m case_studies.prompt_forge.run` |
| WhyBuddy | Task-based model/provider routing | `uv run python -m case_studies.whybuddy.run` |
| Autonomous Debate | Multi-role graph state + checkpoint/resume | `uv run python -m case_studies.autonomous_debate.run` |
| CitizenAssist | Lexical retrieval + source IDs | `uv run python -m case_studies.citizen_assist.run` |
| Math Reasoning | Bounded answer verification; opt-in Docker execution | `uv run python -m case_studies.math_reasoning.run` |

See [provider configuration](../docs/PROVIDER_CONFIGURATION.md) to switch the same scripts to OpenRouter, OpenAI, Anthropic, Google, or local Ollama using `.env`. Live calls require `--live`, an API key where applicable, and can consume quota/credits.

**Sandbox:** `uv run python -m case_studies.math_reasoning.run --sandbox` additionally executes a tiny Python program inside a local Docker container. Pre-pull the configured image (`docker pull python:3.12-slim`) first. Never execute a generated program directly with host Python. A local Docker daemon is not a production-grade multi-tenant security boundary. Read the math case study documentation before using it with untrusted code.

All data are invented educational fixtures. No real addresses, incidents, or private conversational records are used.
