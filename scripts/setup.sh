#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required: https://docs.astral.sh/uv/getting-started/installation/" >&2
  exit 1
fi
if command -v git >/dev/null 2>&1 && [[ ! -d .git ]]; then
  git init
fi
if [[ ! -f uv.lock ]]; then
  echo "Creating uv.lock using the package registry (requires internet on first run)..."
  uv lock
  echo "Commit the generated uv.lock before pushing to GitHub."
fi
uv sync --locked --group dev
uv run --offline --locked python -c 'import applied_ai; print("Installed:", applied_ai.__version__)'
uv run --offline --locked pytest -q
