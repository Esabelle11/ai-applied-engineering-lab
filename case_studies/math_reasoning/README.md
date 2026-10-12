# Math Reasoning — Verification and Isolated Execution

**Problem:** An LLM's numeric answer or generated code must be checked by a separate verifier. Running arbitrary generated code in the host process is unsafe.

**Architecture:** `VerificationLoop` (08) → deterministic arithmetic oracle (08) → optional `DockerPythonSandbox` (08) → compare stdout and exit status. Provider access remains in the SDK (02). No generated code is ever executed in the host Python interpreter.

```sh
# Always works offline, only checks the numeric answer; no code execution:
uv run python -m case_studies.math_reasoning.run

# Execute sample Python in Docker (pre-pull the image once):
docker pull python:3.12-slim
uv run python -m case_studies.math_reasoning.run --sandbox

# Optional live provider (uses model-generated Python code inside Docker):
uv run python -m case_studies.math_reasoning.run --live --sandbox
```

**Test coverage:** `tests/test_phase4_cases.py` covers mock answer verification and simulated sandbox pass/fail. Docker invocation is tested by mocking the Docker CLI; CI does not need Docker or network access. Live real-model behavior and Docker boundary hardening require manual verification.

**Security limitations:** This is a *local educational Docker boundary* (no network, read-only filesystem, dropped capabilities, unprivileged user, resource limits), **not** a production multi-tenant sandbox. Host Docker daemon security, Docker socket permissions, kernel/VM isolation, image provenance, log/output growth, orphan-container cleanup after interrupted clients, and adversarial testing require additional hardening. Do not accept arbitrary users' code on a publicly accessible service with this example.

**Verification limitations:** The independent oracle for the single synthetic problem is hardcoded (`400`). Successful execution doesn't establish general mathematical correctness. Generated Python may be wrong or contain harmful behavior; explicit opt-in and isolation are necessary.
