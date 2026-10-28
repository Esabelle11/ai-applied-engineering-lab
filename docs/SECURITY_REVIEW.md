# Security Review — Release Candidate

**Review scope:** static source/configuration review of the current codebase; **not** a penetration test, independent audit, or claim of public-hosting readiness. No credentials were used.

| Area | Observed guardrail | Risk / remaining work |
| --- | --- | --- |
| Secrets | `.env*` ignored except example, server reads credentials, local tracked-file and source-pattern checks | A simple scanner cannot catch all credentials, files in earlier commits, or secrets hidden in binary assets. Run Gitleaks on full Git history before tagging. Revoke any previously exposed keys. |
| Provider calls | No live operation by default; `.env` provider/model selected on server; explicit `--live` and key required | Third-party endpoint/model availability and error messaging must be smoke-tested. Billing caps are not enforced by the project. |
| Playground | Localhost default, optional bearer token, same-origin checks, CSP, curated allowlist, input limits, process quotas | Not an Internet-facing auth system: no TLS, user accounts, distributed quotas, persistent audit logging, CSRF guarantees behind reverse proxies, or billing limits. Never deploy publicly unchanged. |
| Docker execution pattern | Separate CLI, pre-pulled image, no network, read-only root, unprivileged user, dropped capabilities, memory/CPU/pid limits | Host Docker daemon is trusted and often privileged; image `python:3.12-slim` is not digest-pinned; no per-tenant isolation attestation, complete seccomp verification, or comprehensive adversarial tests. `subprocess.run` buffers output before truncation, allowing large output memory use. Restrict to trusted local experimenters until hardened. |
| Prompt/RAG | Small deterministic sample documents; no untrusted webpage fetch by default | Prompt-injection resistance is not guaranteed. Retrieval demos use lexical search and citations, not independent fact verification. |
| Dependencies | `pyproject.toml` separates extras; CI planned to audit locked dependencies | **Blocked until `uv.lock` exists and vulnerability audit passes**. Lock updates and external provider upgrades must be reviewed. |
| Supply chain | GitHub workflow `permissions: contents: read` and CI checks; releases not auto-published | Review third-party action pins and enable branch/tag protection on GitHub. Ensure release workflow is green before distribution. |

## Commands to run and retain as evidence

```bash
python scripts/security_static_check.py
python scripts/check_no_secrets.py
# Requires the real uv.lock and network:
uv export --locked --all-extras --all-groups --no-emit-project --format requirements.txt --no-hashes -o /tmp/ai-lab-audit-requirements.txt
uvx --from pip-audit pip-audit --no-deps -r /tmp/ai-lab-audit-requirements.txt
# Run Gitleaks across repository history separately (and GitHub security workflow).
```

The export includes the package's optional provider and playground dependencies plus development tools. Auditing only the minimal install would miss vulnerabilities in optional features. Record scanner versions, completion time, affected package(s), and remediation; report a failing scan rather than labeling it 'clean'.

## Approval checklist

- [x] Static code/config review documented; no unrestricted Python execution endpoint observed.
- [x] Offline source-pattern and tracked-file checks supplied, with tests.
- [ ] Independent Git history secret scan completed against the actual repository.
- [ ] Locked dependency vulnerability scan completed with zero untriaged findings.
- [ ] Docker sandbox hardening and output-buffer risk reviewed against intended threat model.
- [ ] GitHub supported-OS/Python matrix green and release SHA recorded.
- [ ] Optional real-provider and Docker smoke tests reviewed if advertised as validated.

**Release posture:** pending. Do not claim secure public multi-tenant hosting; keep sandbox usage local and opt-in.
