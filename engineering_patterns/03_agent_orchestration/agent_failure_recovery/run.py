"""Bound a retryable agent operation and retain its recovery history."""

from __future__ import annotations

from applied_ai.orchestration import RecoveryResult, run_with_recovery


def recover_transient_work() -> RecoveryResult:
    attempts = 0

    def operation() -> str:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise ConnectionError("temporary provider failure")
        return "recovered answer"

    return run_with_recovery(operation, max_attempts=2, retryable=(ConnectionError,))


def main() -> None:
    result = recover_transient_work()
    print("result: ", result)
    print(f"{result.value} after {result.attempts} attempts")


if __name__ == "__main__":
    main()
