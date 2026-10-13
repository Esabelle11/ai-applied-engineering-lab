# Phase 6 — Optional Interactive Playground

**Version:** 0.7.0 · **Status:** Local reference implementation, not a hosted production application.

## Purpose

A small optional UI makes the existing handbook, SDK, and Phase 5 evidence more approachable. There is **no change** to the importable `applied_ai` API, the Phase 4 case-study CLI, or the Phase 5 benchmark CLI. Browser requests enter through a defined FastAPI boundary and can execute only named, preapproved SDK-backed examples.

## Setup

From the repository root, with Python 3.12+ and uv installed:

```bash
uv lock
uv sync --locked --group dev --extra playground --extra providers
uv run --locked python -m apps.playground.backend
```

Open **[http://127.0.0.1:8765](http://127.0.0.1:8765)**. The server binds to loopback by default. No API key, Docker, Node.js, or build step is necessary for the offline demos. Frontend assets are first-party static HTML/CSS/JS; they do not load external scripts.

Run all offline checks:

```bash
uv run --locked pytest -q
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy src
uv run --locked python scripts/validate_patterns.py
uv run --offline --locked python scripts/run_all_patterns.py
uv run --offline --locked python scripts/run_all_case_studies.py
uv run --offline --locked python scripts/run_benchmarks.py
```



## UI navigation


| View            | Feature                                             | Source                                                 |
| --------------- | --------------------------------------------------- | ------------------------------------------------------ |
| Overview        | Status, demos, quota, architecture boundaries       | Whitelisted server registry                            |
| Pattern library | Search and filter handbook manifests                | `engineering_patterns/**/pattern.yaml` (metadata only) |
| Playground      | Run six curated offline examples                    | Existing `applied_ai.*` SDK utilities                  |
| Compare         | Retry and prompt-construction side-by-side examples | Same synthetic controls per branch                     |
| Evidence        | Published Phase 5 metric tables and SHA256 hashes   | `benchmarks/reports/baseline_offline/`                 |


Available playground examples: provider-neutral generation; prompt-template rendering; transient 429/retry recovery; lexical retrieval with source IDs; three-node state graph; and fixed-fixture math verification. The math example **only accepts** `Compute 17 * 23 + 9` and will reject other input, rather than claim general math accuracy. Retrieval is **lexical**, not embedding/vector retrieval. Evidence tables contain **synthetic observations**, not live-model benchmark claims.

## API boundaries


| Method | Path            | Policy                                                       |
| ------ | --------------- | ------------------------------------------------------------ |
| GET    | `/api/health`   | Minimal status only                                          |
| GET    | `/api/settings` | Authorization; returns flags and remaining quota, never keys |
| GET    | `/api/catalog`  | Authorization; read-only sanitized metadata, no file paths   |
| GET    | `/api/reports`  | Authorization; committed offline summaries only              |
| POST   | `/api/run`      | Authorization, input validation, allowlist, run-unit quota   |
| POST   | `/api/compare`  | Authorization, input validation, allowlist, two-unit quota   |
| GET    | `/static/...`   | Only bundled frontend assets                                 |


`POST /api/run` JSON: `{"example_id":"generation", "value":"Explain RAG", "live":false}`. The response includes `result` and process-local `quota`. `POST /api/compare` JSON: `{"comparison_id":"retry_recovery", "value":"Explain reliability"}`. Compares **synthetic fixtures** only; this does not establish production superiority. Inputs are at most 500 characters; response tokens on optional live generation are capped at 512. The budget leaves room for reasoning-model output before the bounded reply. The UI displays attempt counts, wall-clock sample latency, execution trace, validation outcomes and usage when available. **Missing measured cost is null, not $0.**

## Access & secrets

The server binds to `127.0.0.1` by default, and tokenless API calls are rejected for non-loopback clients. For shared-machine use or any non-loopback binding, set a secret `PLAYGROUND_TOKEN` of at least 16 random characters in your shell environment. Avoid exposing the app on a public network or placing it behind a proxy without additional TLS, authentication, per-user budgets, and request monitoring.

```bash
export PLAYGROUND_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
uv run --locked python -m apps.playground.backend --host 127.0.0.1
```

Use the **Access** button to supply a token; the browser keeps it in JavaScript memory only, not in cookies, storage, or URL query strings. The server never returns provider credentials to the frontend. API write operations reject cross-origin requests, and pages set restrictive CSP and other security headers.

## Live providers (explicit opt-in)

Offline mode remains available even if `.env` points at OpenRouter, OpenAI, Anthropic, Gemini, or Ollama. To authorize live generation of **only** the two supported text examples:

```bash
# .env (never commit it)
AI_LAB_PROVIDER=openrouter
AI_LAB_MODEL=nvidia/nemotron-3.5-lightning:free
OPENROUTER_API_KEY=...  # real secret

# shell environment: use a long random token
export PLAYGROUND_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
export PLAYGROUND_TOKEN="$(uv run python -c 'import secrets; print(secrets.token_urlsafe(32))')"
printf %s "$PLAYGROUND_TOKEN" | pbcopy
printf 'token length: %s\n' "${#PLAYGROUND_TOKEN}"
uv run --locked python -m apps.playground.backend --allow-live

# or OPENROUTER_API_KEY is set in .env file
uv run --env-file .env --locked --extra playground python -m apps.playground.backend --allow-live
```



Use the **Access** button and enable the live toggle only after the server has started with `--allow-live`. The provider/model are read server-side from `.env`; the web client cannot change the provider endpoint, supply an arbitrary model, inspect keys, or run other arbitrary operations. Live calls may incur costs and quotas; even models with `:free` names can be unavailable or rate-limited. The server never makes live requests on page load. SDK provider-specific failures return normalized categories rather than upstream credential-bearing bodies.

**Budget limitations:** There is a process-local counter (80 execution units by default), per-request maximum 500 input characters, two concurrent handlers, and a per-attempt provider timeout. These are **not** distributed rate limits, a billing cap, or sufficient safeguards for a public multi-user service. Restart resets quotas. Requests already in flight may continue within provider timeouts. No background worker or persistent queue is shipped.

## Code execution policy

**The playground has no code-execution endpoint.** It never runs arbitrary scripts from `engineering_patterns/` or evaluates user/model Python. Generated code is *not* run inside the FastAPI worker. The Phase 4 math sandbox remains a **separate opt-in Docker CLI feature**, outside the browser entirely. Its existing Docker isolation constraints are not presented as hardened multi-tenant security. A future hosted execution system would require isolated sandbox workers, explicit tool policies, and per-user budgets.

## Architecture and test coverage

```text
Browser (static JS; no secrets)
    | GET catalog/reports; POST approved examples
    v
FastAPI app (auth, same-origin checks, input contracts, quotas, concurrency)
    |
    +--> curated service.execute / service.compare (explicit allowlist)
    |       +--> PromptTemplate / MockProvider / ReliableProvider
    |       +--> LexicalRetriever / StateGraph / VerificationLoop
    |       +--> optional provider factory, only after live opt-in
    |
    +--> read-only handbook metadata / published benchmark summaries

NO subprocess, Docker, exec(), dynamic import, arbitrary script runner,
vector DB, secrets returned to browser, or SDK-to-UI dependency.
```

`tests/test_phase6_playground.py` covers offline execution, trace evidence, validation, catalog discovery, API status codes, access token checks, origin checks, process quotas, remote denial, and live opt-in. This is a local demo, not a third-party penetration test or production security audit.

## Definition of done

- [x] Metadata discovery API uses handbook manifests, not executed scripts.
- [x] Curated input parameters, predictable runs, traces, validation, and honest missing-cost labels.
- [x] Two synthetic side-by-side comparisons and Phase 5 baseline viewer.
- [x] Server-side keys, default-off live providers, process quota, concurrent execution limit.
- [x] No untrusted Python execution from the web server.
- [x] Existing SDK, CLI, patterns, case studies, and benchmarks unchanged.
- [ ] Optional live-provider interoperability verified with real credentials on a trusted local machine.
- [ ] Ruff, mypy, GitHub Actions and a real browser smoke check verified outside this environment.