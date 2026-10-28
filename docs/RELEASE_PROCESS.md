# First Release Runbook — v0.8.0 Candidate

**Status: PRE-TAG CANDIDATE.** This ZIP intentionally contains no fabricated lockfile and no Git tag. The first release is allowed only after documented exit criteria are met. See [SECURITY_REVIEW.md](SECURITY_REVIEW.md).

## 1. Prepare (a network-enabled development machine)

```bash
uv lock
uv sync --locked --group dev --extra providers --extra playground
uv run --locked python scripts/generate_catalog.py --check
uv run --locked python scripts/generate_api_reference.py --check
uv run --locked python scripts/validate_patterns.py
uv run --locked python scripts/release_check.py --strict
```

Do not create an empty or hand-written `uv.lock`. Commit the actual resolved lock with `pyproject.toml` and the release sources. Confirm your branch contains no credentials, generated `.env`, proprietary data or model outputs.

## 2. Run complete quality and reproducibility checks

```bash
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy src
uv run --offline --locked pytest -q
uv run --offline --locked python scripts/run_all_patterns.py
uv run --offline --locked python scripts/run_all_case_studies.py
uv run --locked python scripts/check_no_secrets.py
uv run --locked python scripts/security_static_check.py
uv build
```

Run the GitHub Actions test matrix on Linux/macOS/Windows with Python 3.12/3.13. Verify the *actual* security workflow succeeds: locked dependency vulnerability audit, source and Git-history secret scan. Do not imply local offline tests prove those external steps ran.

## 3. Security and external-provider review

Review [SECURITY_REVIEW.md](SECURITY_REVIEW.md); record outstanding risks with owners. Do not publish credentials or raw model prompts. Only if you intend to claim live-provider validation, separately run an opt-in smoke test with a small budget and document which model/version/date was used. For sandbox claims, use a trusted Docker workstation and assess output/resource limits before accepting unknown user code.

## 4. Confirm public API, artifacts and release notes

- Review [API_REFERENCE.md](API_REFERENCE.md) for all `applied_ai.__all__` imports.
- Check that `src/applied_ai/__init__.py`, `pyproject.toml`, and `CHANGELOG.md` all say `0.8.0`.
- Include source archive, source distribution and wheel (built via `uv build`) only after tests pass.
- Check the wheel can be installed into a clean Python 3.12/3.13 environment and run `import applied_ai`.

## 5. Tag and publish *only after green gates*

From the clean, reviewed commit on `main` (after all required GitHub checks are green):

```bash
git status --short                # Must be clean
git log -1 --oneline              # Record SHA
git tag -a v0.8.0 -m "Applied AI Engineering Lab v0.8.0"
git push origin v0.8.0
```

The tag build workflow checks version/tag consistency, runs tests and builds artifacts; publishing a GitHub Release or PyPI package is a separate **manual** action after that workflow is green. Verify the tag points to the same previously tested SHA. Do not overwrite signed/released tags. If checks fail, fix issues and create a new version/tag instead of pretending the previous tag passed.

## 6. Traceability record

| Evidence | Required |
| --- | --- |
| Source SHA and release tag | SHA, signed/annotated tag link |
| Lockfile SHA256 and Python/tool versions | Saved in release notes |
| CI workflow results | URLs for matrix/security/tag jobs |
| Dependency and secret scans | Dates, tool versions, findings/resolutions |
| Build outputs | Wheel and sdist hashes |
| Sample run | Commit/config hashes and limitations |

The current candidate intentionally leaves these values unfilled until verified. No action in the supplied package pushes to GitHub or changes your repository remotely.
