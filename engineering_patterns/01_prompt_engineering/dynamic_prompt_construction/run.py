"""Construct a prompt from prioritized sections under a deterministic character budget."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PromptSection:
    name: str
    content: str
    priority: int = 0

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.content.strip() or self.priority < 0:
            raise ValueError("Sections need a name, content, and non-negative priority")


@dataclass(frozen=True, slots=True)
class DynamicPrompt:
    text: str
    included_sections: tuple[str, ...]
    omitted_sections: tuple[str, ...]


def build_dynamic_prompt(
    goal: str, sections: tuple[PromptSection, ...], *, max_chars: int
) -> DynamicPrompt:
    """Keep higher-priority context first while reporting exactly what was excluded."""
    if not goal.strip() or max_chars < len(goal):
        raise ValueError("goal must be non-empty and max_chars must fit the goal")
    text = f"Goal:\n{goal.strip()}"
    included: list[str] = []
    omitted: list[str] = []
    for section in sorted(sections, key=lambda item: (-item.priority, item.name)):
        addition = f"\n\n[{section.name}]\n{section.content.strip()}"
        if len(text) + len(addition) <= max_chars:
            text += addition
            included.append(section.name)
        else:
            omitted.append(section.name)
    return DynamicPrompt(text, tuple(included), tuple(omitted))


def main() -> None:
    prompt = build_dynamic_prompt(
        "Answer using the most relevant context.",
        (
            PromptSection("policy", "Cite source IDs.", 2),
            PromptSection("history", "Older chat context.", 0),
        ),
        max_chars=100,
    )
    print(prompt.text)
    print(f"Omitted: {', '.join(prompt.omitted_sections) or 'none'}")


if __name__ == "__main__":
    main()
