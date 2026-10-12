"""Executable, offline Applied AI handbook pattern."""

from applied_ai import MockProvider
from applied_ai.reasoning import VerificationLoop


def main() -> None:
    question = "Compute 6 times 7"
    retry = "Previous answer failed independent verification. Try again."
    mock = MockProvider(responses={question: "41", f"{question}\n{retry}": "42"})
    result = VerificationLoop(mock, "mock", max_attempts=3).solve(
        question, verifier=lambda value: value.strip() == str(6 * 7)
    )
    print(f"Verified={result.accepted}; attempts={result.attempts}; answer={result.answer}")


if __name__ == "__main__":
    main()
