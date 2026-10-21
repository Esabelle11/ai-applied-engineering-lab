"""Few-shot prompt construction with validated, clearly delimited examples."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Example:
    input: str
    output: str

    def __post_init__(self) -> None:
        if not self.input.strip() or not self.output.strip():
            raise ValueError("Few-shot examples require non-empty input and output")


def build_few_shot_prompt(instruction: str, examples: tuple[Example, ...], query: str) -> str:
    """Separate demonstrations from the final task, avoiding ambiguous prose concatenation."""
    if not instruction.strip() or not examples or not query.strip():
        raise ValueError("instruction, at least one example, and query are required")
    blocks = [f"Instruction:\n{instruction.strip()}", "Examples:"]
    for index, example in enumerate(examples, 1):
        blocks.append(
            f'<example id="{index}">\nInput: {example.input}\nOutput: {example.output}\n</example>'
        )
    blocks.append(f"Now solve this new input:\nInput: {query.strip()}\nOutput:")
    return "\n\n".join(blocks)


def main() -> None:
    print(
        build_few_shot_prompt(
            "Convert a number to an English word.",
            (Example("1", "one"), Example("2", "two")),
            "3",
        )
    )


if __name__ == "__main__":
    main()
