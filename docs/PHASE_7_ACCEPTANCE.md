# Phase 7 — Documentation and Release (D7)

**Candidate version:** 0.8.0. This document distinguishes implemented release preparation from externally verified release completion.

| Requirement | Local deliverable | Status |
| --- | --- | --- |
| Public API/version/changelog | `applied_ai.__all__`, generated API reference, `pyproject.toml`, changelog | Implemented; pre-tag |
| Design decisions/backward compatibility | `ARCHITECTURAL_DECISIONS.md`, `COMPATIBILITY.md` | Implemented |
| Generated pattern/API reference | `generate_catalog.py`, `generate_api_reference.py`, committed outputs, `--check` | Implemented |
| CI for supported Python | `.github/workflows/ci.yml`, 3 OS × 2 Python versions | Configured; execution pending |
| Dependency & secrets checks | Static scan, secret history workflow, locked-dependency audit workflow | Offline scan can run; external audits pending |
| Sandbox security review | `SECURITY_REVIEW.md` threat boundaries and open risks | Documented; hardening pending |
| Contribution templates | PR template + pattern and benchmark issue templates | Implemented |
| Tagged first release | Manual gated release runbook and tag workflow | **Not tagged; blocked on green checks/lockfile** |

## Local evidence

Run `python scripts/release_check.py` for metadata only; `python scripts/release_check.py --strict` must reject a missing `uv.lock`. Execute `python scripts/generate_catalog.py --check` and `python scripts/generate_api_reference.py --check`. Offline tests may pass without external dependencies, but they **do not** prove the security or CI jobs ran.

## Signoff before tag

- [ ] Genuine `uv.lock` committed and `uv sync --locked` succeeds from clean checkout.
- [ ] Full Python 3.12/3.13 CI matrix green on Linux/macOS/Windows.
- [ ] `ruff`, `mypy`, tests, pattern validation, benchmarks and wheel install pass.
- [ ] Locked dependency audit and Git history secret scan green; findings documented.
- [ ] Security review issues addressed/accepted for stated local development scope.
- [ ] `v0.8.0` annotated tag created on tested SHA, tag workflow green.

**D7 status: release candidate prepared, NOT fully released.**
