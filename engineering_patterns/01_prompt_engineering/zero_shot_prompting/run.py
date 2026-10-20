"""Build and execute a bounded zero-shot prompt without hidden examples."""

from __future__ import annotations

from applied_ai import LLMRequest, Message, MockProvider
from applied_ai.core.protocols import LLMProvider


def build_zero_shot_messages(
    instruction: str, task_input: str, *, output_format: str = "plain text"
) -> tuple[Message, ...]:
    """Create a model-neutral instruction and user task with explicit output expectations."""
    if not all(
        isinstance(item, str) and item.strip() for item in (instruction, task_input, output_format)
    ):
        raise ValueError("instruction, task_input, and output_format must be non-empty text")
    return (
        Message("system", f"{instruction.strip()}\nReturn {output_format.strip()}"),
        Message("user", task_input.strip()),
    )


def execute_zero_shot(provider: LLMProvider, model: str, instruction: str, task_input: str) -> str:
    """Execute one explicit generation call; retries and grading are separate concerns."""
    response = provider.generate(LLMRequest(model, build_zero_shot_messages(instruction, task_input)))
    return response.text


def main() -> None:
    question = "Classify this review as positive or negative: The battery lasts all day."
    provider = MockProvider(responses={question: "positive"})
    print(execute_zero_shot(provider, "mock", "Classify sentiment using one lowercase word", question))


if __name__ == "__main__":
    main()
