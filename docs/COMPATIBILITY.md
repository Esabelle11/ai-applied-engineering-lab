# Versioning and Compatibility

The first release candidate is **0.8.0**. It is a **pre-1.0** Python library; the number is the project/package version, not a completed production certification. Its source is `pyproject.toml` and `src/applied_ai/__init__.py`. Both must agree.

## Supported environments

- **Python 3.12 and 3.13** are the CI targets; Python >=3.12 is declared, but newer unreleased versions are not promised.
- Linux, macOS and Windows are CI targets for offline Python functionality.
- Optional playground requires `--extra playground`, binds to localhost by default, and is not a multi-user hosted service.
- Docker is optional and only used by the explicit math sandbox CLI; Docker installation/image and security posture are not verified by regular tests.
- OpenRouter, OpenAI, Anthropic, Google and Ollama provider configurations are optional. Live model capabilities, endpoint contracts, pricing and availability can change without this project's release.

## Public API promise (pre-1.0)

The canonical documented import surface is `applied_ai.__all__`, reproduced in [API_REFERENCE.md](API_REFERENCE.md). It contains common messages, request/response types, provider abstractions, and reliability types. Backwards-incompatible changes **can occur in a minor release before 1.0**, but must be recorded in CHANGELOG and migration instructions. Micro releases aim to preserve public semantics and fix bugs.

`src/applied_ai/` internal modules and CLI flags are not guaranteed stable unless explicitly documented. `engineering_patterns/` and `case_studies/` are instructional examples, not API guarantees. YAML pattern manifests are an educational metadata schema and may evolve separately from Python package versioning.

### Changes requiring review

- `LLMRequest`/`LLMResponse` fields or validation; exception categories and retryability.
- Provider capability contract and opt-in provider API behavior.
- Reliability wrapper's deadlines, attempts, and fallback semantics.
- Python version, dependency extras and lockfile resolution.
- Security boundaries (especially sandbox and playground access controls).

Deprecations should have a documented replacement, a test, and a changelog entry. Do not silently downgrade required capabilities, expand live permissions, or remove default-off safety controls.

## Dependency reproducibility

Commit the real `uv.lock` produced by `uv lock` from a network-enabled developer machine. All CI installs use `uv sync --locked`. The lock must include optional extras and dev groups; changing `pyproject.toml` requires intentionally regenerating the lock. **This distributed ZIP has no lockfile:** it is not yet a reproducible, tagged release.
