# Case studies

These are *small synthetic reference implementations*, **not** copies of the original products. Their components import `applied_ai` from `src/` and compose previously tested engineering patterns. By default **no API calls** occur.

| Study | Demonstrates | Offline command |
|---|---|---|
| Prompt Forge | Live prompt linting + captured portfolio replay | `uv run python -m case_studies.prompt_forge.run --replay` |
| WhyBuddy | Question → script → images, TTS narration, and a learning video | `uv run python -m case_studies.whybuddy.run --replay` |
| Autonomous Debate | Multi-role graph state + checkpoint/resume | `uv run python -m case_studies.autonomous_debate.run` |
| CitizenAssist | One LLM intake decision + approved local routing | `uv run python -m case_studies.citizen_assist.run --replay` |
| Loop Tool Agent | Bounded LLM/Python-tool loop with answer consensus | `uv run --extra local-kernel python -m case_studies.loop_tool_agent.run --live --trusted-local-kernel` |

See [provider configuration](../docs/PROVIDER_CONFIGURATION.md) to switch the same scripts to OpenRouter, OpenAI, Anthropic, Google, or local Ollama using `.env`. Live calls require `--live`, an API key where applicable, and can consume quota/credits.

**Local execution:** Loop Tool Agent runs model-generated Python in a local Jupyter kernel only when you explicitly pass `--trusted-local-kernel`. This is for trusted local experiments, not a security sandbox for untrusted users or arbitrary model output.

Data are invented educational fixtures except the Prompt Forge portfolio replay,
which is a user-provided captured LLM result. No real addresses, incidents, or
private conversational records are used.
