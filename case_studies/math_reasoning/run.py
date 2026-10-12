"""A bounded math verifier; --sandbox enables real, isolated Python execution.

Never execute LLM code locally. Docker must be available and the image pre-pulled.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from typing import Protocol

from applied_ai.core import LLMRequest, Message
from applied_ai.execution import DockerPythonSandbox, SandboxResult
from applied_ai.providers.factory import ProviderFactory
from applied_ai.reasoning import VerificationLoop, VerificationResult

QUESTION = "Compute 17 * 23 + 9. Reply with only the integer."
EXPECTED = 400  # Independent deterministic oracle for this synthetic fixture.


class Sandbox(Protocol):
    def run(self, code: str) -> SandboxResult: ...


@dataclass(frozen=True, slots=True)
class MathResult:
    verification: VerificationResult
    sandbox: SandboxResult | None
    sandbox_verified: bool | None


def run(*, allow_live: bool = False, sandbox: Sandbox | None = None) -> MathResult:
    selected = ProviderFactory().create(allow_live=allow_live, mock_text=str(EXPECTED))
    provider = selected.provider
    try:
        result = VerificationLoop(provider, selected.model, max_attempts=2).solve(
            QUESTION,
            lambda answer: bool(re.fullmatch(r"\s*400\s*", answer)),
        )
        if sandbox is None:
            return MathResult(result, None, None)
        # In mock mode this is a deterministic Python sample. Live mode allows the
        # model to propose code; it *only* executes in the Docker isolation boundary.
        if provider.name == "mock":
            code = "print(17 * 23 + 9)"
        else:
            code = provider.generate(
                LLMRequest(
                    selected.model,
                    (
                        Message(
                            "user",
                            "Write Python code that prints the result of 17 * 23 + 9. Return code only, no Markdown.",
                        ),
                    ),
                )
            ).text
            if code.startswith("```"):
                code = re.sub(r"^```(?:python)?\s*|\s*```$", "", code).strip()
        execution = sandbox.run(code)
        correct = execution.exit_code == 0 and execution.stdout.strip() == str(EXPECTED)
        return MathResult(result, execution, correct)
    finally:
        close = getattr(provider, "close", None)
        if callable(close):
            close()


if __name__ == "__main__":
    result = run(
        allow_live="--live" in sys.argv,
        sandbox=DockerPythonSandbox() if "--sandbox" in sys.argv else None,
    )
    print("Verified answer:", result.verification.accepted, result.verification.answer)
    if result.sandbox is None:
        print("Code execution disabled by default; pass --sandbox with Docker installed.")
    else:
        print("Sandboxed Python verified:", result.sandbox_verified)
        print("Sandbox output:", result.sandbox.stdout.strip())
