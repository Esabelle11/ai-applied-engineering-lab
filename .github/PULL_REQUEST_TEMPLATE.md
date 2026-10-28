## Change summary
Explain engineering need, pattern/API touched, and expected observable behavior.

## Scope and compatibility
- [ ] Public SDK contract changes are documented with migrations if needed.
- [ ] New provider or pattern features have explicit capability checks and offline alternatives.
- [ ] No secrets, user conversation data, proprietary datasets or untrusted executable payloads are committed.

## Evidence
- [ ] `ruff check`, `ruff format --check`, `mypy src`.
- [ ] `pytest -q` and `validate_patterns.py`.
- [ ] Added/updated deterministic normal and failure-path tests.
- [ ] Updated pattern metadata/catalog and API docs (`--check` passes).
- [ ] Performance claims have fixed controls, raw inputs, run metadata, and limitations.

## Risks and rollback
Security, billing, sandbox, compatibility, and migration notes.
