# Applied AI Engineering Lab

**An executable Python engineering handbook + reusable SDK** for LLMs, agents, RAG, reliable integration and verification. Categories are independent learning units, **not** a continuous application execution pipeline.

**Current state: release candidate (**`0.8.0`**), not yet a tagged release.** The package and offline materials can be tested without API keys. The distributable ZIP does not include a real `uv.lock`, so reproducible clean-install/CI claims await lockfile generation and GitHub verification. See the [release process](docs/RELEASE_PROCESS.md).

## Start here

Requirements: Python **3.12 or 3.13**, [uv](https://docs.astral.sh/uv/), Git. CI targets Linux, macOS, Windows; Python 3.12 and 3.13. From a clean extracted checkout:

```bash
# Generate and COMMIT the genuine lockfile on a machine with PyPI access
uv lock
uv sync --locked --group dev --extra providers --extra playground

uv run --offline --locked pytest -q. 
or 
uv run --locked python -m pytest -q

uv run --offline --locked python scripts/run_all_patterns.py
uv run --offline --locked python scripts/run_all_case_studies.py
```

The default provider is a **deterministic offline mock**. To change providers, set `AI_LAB_PROVIDER` and `AI_LAB_MODEL` in `.env` and supply the matching key. Live examples **must** be explicitly authorized with `--live`. OpenRouter, OpenAI, Anthropic, Google and local Ollama adapters are available via the optional `providers` extra; capabilities and model availability differ. See [provider configuration](docs/PROVIDER_CONFIGURATION.md).

## Handbook architecture


| Directory                                                 | Responsibility                                                                             |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| `[engineering_patterns/](engineering_patterns/README.md)` | Runnable patterns in nine independent categories                                            |
| `[src/applied_ai/](src/applied_ai/)`                      | Shared importable Python SDK; no dependency on tutorials/UI                                |
| `[case_studies/](case_studies/README.md)`                 | Four SDK-composed examples: Prompt Forge, WhyBuddy, Debate, and CitizenAssist              |
| `[apps/playground/](docs/PLAYGROUND.md)`                  | Optional localhost FastAPI + static UI; approved examples only                             |
| `[docs/API_REFERENCE.md](docs/API_REFERENCE.md)`          | Generated stable import surface (`applied_ai.__all__`)                                     |
| `[docs/PATTERN_CATALOG.md](docs/PATTERN_CATALOG.md)`      | Generated pattern catalog and quick links                                                  |




### The nine engineering-pattern categories

**01 Prompt Engineering**, **02 Model Integration**, **03 Agent Orchestration**, **04 Knowledge & Context**, **05 Reliability Engineering**, **06 Evaluation & Observability**, **07 Optimization**, and **08 Reasoning & Execution**. Numbered folders are not importable Python modules or dependency ordering.

**09 LangChain & LangGraph** contains optional framework-specific implementations. Install them with `uv sync --extra agent-frameworks`.

## Provider-neutral generation example

```python
from applied_ai import LLMRequest, Message, MockProvider

response = MockProvider(default_text="Hello!").generate(
    LLMRequest("mock-model", (Message("user", "Hi"),))
)
print(response.text)
```

Retries, fallback and rate limiting are opt-in via `ReliableProvider`. The base `generate()` contract is synchronous; threaded examples are not native async HTTP. Lexical retrieval examples are not vector-search claims. The Loop Tool Agent's local Jupyter execution requires explicit opt-in and is **not** hardened for hostile multi-tenant code execution.

## Optional browser playground

```bash
uv run --locked --extra playground python -m apps.playground.backend
# Open http://127.0.0.1:8765
```

Live mode requires an explicitly authorized server start and a long random `PLAYGROUND_TOKEN`. For the token to reach the FastAPI process, export it in the **same shell** or launch via `uv run --env-file .env --locked ...` (a preexisting shell variable may override `.env`). The Access dialog is for the playground token, not your provider API key. See the [playground security/access guide](docs/PLAYGROUND.md).

## Development and release verification

```bash
uv run --locked ruff check .
if have error:
uv run --locked ruff check . --fix --unsafe-fixes

uv run --locked ruff format --check .
if have error:
uv run --locked ruff format .

uv run --locked mypy src
uv run --locked python scripts/validate_patterns.py
uv run --locked python scripts/generate_catalog.py --check
uv run --locked python scripts/generate_api_reference.py --check
uv run --locked python scripts/security_static_check.py
uv run --locked python scripts/check_no_secrets.py
uv run --locked python scripts/release_check.py --strict
uv build
```

**Before tagging**: run GitHub CI for every supported OS/Python combination; run the dependency and Git-history secret scans; inspect [sandbox/security review](docs/SECURITY_REVIEW.md); follow the gated [release runbook](docs/RELEASE_PROCESS.md). Do not interpret a locally green mock suite as live-provider validation, vulnerability clearance, or a successful GitHub run.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md), [compatibility policy](docs/COMPATIBILITY.md), [architectural decisions](docs/ARCHITECTURAL_DECISIONS.md), and [Security](SECURITY.md). Add a runnable README, manifest, deterministic test and failure case for each new pattern.
