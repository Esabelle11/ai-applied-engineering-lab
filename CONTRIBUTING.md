# Contributing to Applied AI Engineering Lab

This repository is a **reusable engineering handbook**, not a directory of unrelated chatbot demos. Keep shared implementation under `src/applied_ai` and executable educational material under `engineering_patterns/`.

## First contribution

Clone, install Python 3.12/3.13 and uv, then `uv lock` (only when dependencies change) followed by `uv sync --locked --group dev --extra providers --extra playground`. Run `uv run --offline --locked pytest -q`. **A genuine committed `uv.lock` is required for a release and CI**; do not manufacture a lockfile.

## New engineering pattern

Start from `engineering_patterns/_template/`. Choose an existing numbered category (numbers are organizational), create a standalone README (problem, mechanism, assumptions, alternatives, limits, failure modes), `pattern.yaml`, safe `run.py`, and deterministic tests including a representative failure. Use SDK imports rather than copying core logic into the example; do not require a live key for normal CI. Add a public API migration note if changing documented exports. Run `python scripts/generate_catalog.py` and verify `--check` passes.

## New benchmarks

Submit a question/hypothesis, manifest/config and dataset hashes, matched inputs/controls, seed when applicable, raw observations, aggregations, failure and negative outcomes, sample sizes and limitations. Synthetic fixtures must never be presented as measured live-model performance. Use issue template `benchmark_submission.md`.

## Quality gate

```bash
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy src
uv run --offline --locked pytest -q
uv run --locked python scripts/validate_patterns.py
uv run --locked python scripts/generate_catalog.py --check
uv run --locked python scripts/generate_api_reference.py --check
uv run --locked python scripts/security_static_check.py
uv run --locked python scripts/check_no_secrets.py
```

Do not include `.env`, keys, proprietary data, customer transcripts, unsafe Python snippets runnable by the web server, or unbounded live-provider calls. Live examples must be opt-in. Describe security and compatibility implications and include rollback guidance in the pull request template.
