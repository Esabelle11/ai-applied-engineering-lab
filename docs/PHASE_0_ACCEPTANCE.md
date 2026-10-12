# Phase 0 — Acceptance and Verification

**Current state:** locally validated using the installed Python 3.13 runtime.
A full D0 pass requires generating `uv.lock` with network access, installing
all dev tools, and observing a green GitHub Actions run. These steps were not
available in the authoring environment. Do not claim CI is passing yet.

## Exit criteria

1. A fresh contributor installs the project with `uv sync --locked --group dev`.
2. `uv run python -c "import applied_ai"` succeeds.
3. `uv run --offline --locked pytest -q` passes with no API credentials.
4. `uv run --locked ruff check .` passes.
5. `uv run --locked ruff format --check .` passes.
6. `uv run --locked mypy src` passes.
7. `uv run --locked python scripts/validate_patterns.py` passes.
8. `uv build` creates wheel and sdist.
9. `.env` remains untracked; no real credentials are included.
10. GitHub CI reports success after first push (requires GitHub verification).

## Verification completed locally

- `pip install --no-index --no-build-isolation -e .`: successful install.
- `python -m pytest -q`: **14 passed**, without external API calls.
- `python scripts/validate_patterns.py`: passed.
- `python -m compileall -q src tests scripts engineering_patterns`: passed.
- `uv build --offline --no-build-isolation` using installed Python 3.13: built wheel and sdist.
- `uv lock`: **blocked by network access to PyPI**; must be run by contributor.
- `ruff`, `mypy`, GitHub CI: **not executed** here; check after sync.

## Verification scope

Local checks validate Python 3.13 in the current build environment. The CI
matrix is configured for Python 3.12 and 3.13 across Linux, macOS, and Windows;
actual CI results cannot be claimed until the repository is pushed.

## What Phase 0 does not promise

No actual provider API client, multi-model routing, agent orchestration,
reliability middleware, RAG system, or secure execution sandbox is implemented.
