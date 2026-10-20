"""Evaluate a prompt builder against deterministic, labeled test cases."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from applied_ai import LLMRequest, Message
from applied_ai.core.protocols import LLMProvider
from applied_ai.evaluation import exact_match


@dataclass(frozen=True, slots=True)
class PromptTestCase:
    input: str
    expected: str

    def __post_init__(self) -> None:
        if not self.input.strip() or not self.expected.strip():
            raise ValueError("Evaluation inputs and expected outputs must be non-empty")


@dataclass(frozen=True, slots=True)
class PromptEvaluation:
    passed: int
    total: int
    failures: tuple[str, ...]

    @property
    def accuracy(self) -> float:
        return self.passed / self.total if self.total else 0.0


def evaluate_prompt(
    provider: LLMProvider,
    model: str,
    prompt_builder: Callable[[str], str],
    cases: Sequence[PromptTestCase],
) -> PromptEvaluation:
    """Execute each case once and retain input IDs only for failed deterministic checks."""
    if not cases:
        raise ValueError("At least one evaluation case is required")
    failures: list[str] = []
    for case in cases:
        prompt = prompt_builder(case.input)
        response = provider.generate(LLMRequest(model, (Message("user", prompt),)))
        if not exact_match(response.text, case.expected):
            failures.append(case.input)
    return PromptEvaluation(len(cases) - len(failures), len(cases), tuple(failures))


def main() -> None:
    from applied_ai import MockProvider

    def build(item: str) -> str:
        return f"Return uppercase: {item}"

    provider = MockProvider(responses={"Return uppercase: cat": "CAT", "Return uppercase: dog": "DOG"})
    report = evaluate_prompt(provider, "mock", build, (PromptTestCase("cat", "CAT"), PromptTestCase("dog", "DOG")))
    print(f"accuracy={report.accuracy:.0%}")


if __name__ == "__main__":
    main()
