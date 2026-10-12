# Security Policy

## Supported scope

Version **0.8.0** is a **local development/research release candidate** for Python 3.12/3.13. The playground is **not** an Internet-facing multi-tenant AI platform. Docker sandbox execution is opt-in and not independently audited for hostile arbitrary user code.

## Reporting vulnerabilities

Use GitHub's private vulnerability reporting/security advisory feature if the repository owner enables it, or contact the repository maintainers privately through their published contact channel. Do not post working exploits, access tokens, or private data in a public issue. A named security response address has not yet been established; the maintainer should configure one before public release.

## Policy and controls

- Keep provider/API keys server-side; never commit `.env` or log credentials.
- Default to mock/no-network modes; explicit `--live` authorizes external requests that may incur charges.
- Bind the playground to loopback by default. Its bearer token and per-process quotas are **not** substitutes for TLS, user identity or distributed billing guards.
- Never allow untrusted generated Python to run in the FastAPI process. The Docker CLI example restricts network/CPU/memory/processes but is not a complete security boundary for public execution.
- Run `scripts/check_no_secrets.py`, `scripts/security_static_check.py`, Gitleaks across full Git history and `pip-audit` against the **real resolved** `uv.lock` before tagging.
- Revoke any exposed secrets; removing a file from the latest commit does not erase Git history.

See [security review](docs/SECURITY_REVIEW.md) and [release runbook](docs/RELEASE_PROCESS.md) for unverified requirements and residual risks.
