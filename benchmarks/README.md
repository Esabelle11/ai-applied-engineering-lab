# Phase 5 — Reproducible Controlled Experiments

The Phase 5 laboratory is **not an LLM leaderboard**. It tests reusable engineering mechanics with synthetic fixtures before any live-provider exploration. It follows the repo's separation of reusable implementations (`src/applied_ai/`), experiments (`experiments/`), and reproducible evidence (`benchmarks/`).

## Run offline

```bash
uv lock
uv sync --locked --group dev --extra providers
uv run --offline --locked python scripts/run_benchmarks.py
```

Artifacts are written to `benchmarks/reports/generated/<experiment_id>/` (ignored by Git). The committed `benchmarks/reports/baseline_offline/` contains a dated example evidence bundle from the development environment. Re-run locally; wall-clock timings, OS and timestamps will differ. Offline fixture outcomes should be identical.

Run one study:

```bash
uv run --offline --locked python scripts/run_benchmarks.py --experiment retry_strategies
```

For **real LangGraph** (not the Lab's homegrown graph), install the optional extra:

```bash
uv lock
uv sync --locked --group dev --extra providers --extra benchmarks
uv run --locked python scripts/run_benchmarks.py --experiment orchestration_comparison --require-langgraph
```

With no LangGraph package, the runner writes `outcome: unavailable` for it and never reports a fake comparison. The baseline therefore includes only manual Python and SDK graph runs.

## Optional real-provider probe

Copy `.env.example` to `.env`, select a non-mock provider and model, and configure its API key. This script is **not part of CI**.

```bash
uv run --locked python scripts/run_live_benchmark.py --live --max-requests 3
```

The live probe makes at most three outbound model requests, with one request per fixed arithmetic question. It stores strict-match correctness, measured wall time, normalized token usage when provided, and provider/model identity. It does not log API keys or raw model replies. Costs remain `N/A` unless authoritative billing information is available (not implemented). `--live` is required to authorize calls; check quota and billing yourself. OpenRouter's `:free` models may be limited or unavailable.

**Do not compare live runs across days or providers as controlled model rankings.** Service load, backend models/versions, routing, tokenizers, sampling, and rate limits vary. Current providers may not all support deterministic seeds or identical generation parameters.

## Experiment organization

| File | Meaning |
|---|---|
| `experiments/configs/*.json` | Versioned hypothesis, controls, metrics, dataset reference, seed, repeats, limitations |
| `benchmarks/datasets/*.json` | Small synthetic inputs and fault sequences |
| `benchmarks/runners/*.py` | Experiment-specific harnesses calling canonical SDK APIs |
| `src/applied_ai/experimentation/` | Shared validation, aggregation, reporting and provenance |
| `benchmarks/reports/generated/` | Locally generated, machine-readable evidence |
| `benchmarks/reports/baseline_offline/` | Committed reference report and raw observations |

Each offline experiment generates: `manifest_snapshot.json`, `metadata.json`, `results.jsonl`, `summary.json`, `report.md`. The dataset/manifest SHA-256 hashes link each output to exact inputs. Metadata also includes runtime Python/platform, Lab version, concurrency, run date, seed, and optional LangGraph version and Git revision.

## Interpretation and study constraints

**Retry strategies:** Same ordered faults for all four strategies. `no_retry` has one attempt; others have three. The correct metric is *matched expected outcome*, not language-model answer correctness. A permanent authentication failure is expected to **fail fast**. Backoff delays use a deterministic virtual clock, including Retry-After; p50/p95 numbers are *simulated seconds*, not network latency. Successful responses use fixture token counts; failures have unknown upstream usage.

**Orchestration:** Manual Python, the Lab's own `StateGraph`, and (when installed) real LangGraph use the same deterministic four-step topic workflow. No model calls occur. `observed_wall` timing is a tiny local microbenchmark, not a performance claim about actual AI agents. The framework can be unavailable; missing is not scored as failure or success.

**Math:** The first direct answer is scripted; `arithmetic_tool` interprets an LLM-proposed bounded integer expression using a restricted AST; `verification_loop` uses the existing SDK to attempt a correction. Invalid expressions are rejected without arbitrary Python execution. This **does not benchmark the Docker sandbox** or demonstrate LLM reasoning quality. Tool execution and verification can still be wrong. Token usage and per-step latencies are fixtures, not actual provider metrics.

Repetitions verify deterministic results, **not independent draws**. Sample sizes are five to seven unique scenarios, too small for population-level statistical claims. Report negative results alongside positive findings. Missing usage and cost are `N/A`, never zero.

## Validate

```bash
uv run --locked pytest -q
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy src
uv run --locked python scripts/validate_patterns.py
```

The optional LangGraph comparisons and live probes need separate local checks and are not represented as passing in the reference offline baseline.
