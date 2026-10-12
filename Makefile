.PHONY: setup lint format format-check typecheck test test-offline patterns cases benchmarks docs docs-check secrets release-check check build

setup:
	uv sync --locked --group dev --extra providers --extra playground

lint:
	uv run --locked ruff check .

format:
	uv run --locked ruff format .

format-check:
	uv run --locked ruff format --check .

typecheck:
	uv run --locked mypy src

test:
	uv run --locked pytest -q

test-offline:
	uv run --offline --locked pytest -q

patterns:
	uv run --offline --locked python scripts/run_all_patterns.py

cases:
	uv run --offline --locked python scripts/run_all_case_studies.py

benchmarks:
	uv run --offline --locked python scripts/run_benchmarks.py

docs:
	uv run --locked python scripts/generate_catalog.py
	uv run --locked python scripts/generate_api_reference.py

docs-check:
	uv run --locked python scripts/generate_catalog.py --check
	uv run --locked python scripts/generate_api_reference.py --check
	uv run --locked python scripts/validate_patterns.py

secrets:
	uv run --locked python scripts/check_no_secrets.py
	uv run --locked python scripts/security_static_check.py

release-check:
	uv run --locked python scripts/release_check.py --strict

check: lint format-check typecheck docs-check secrets test-offline

build:
	uv build
