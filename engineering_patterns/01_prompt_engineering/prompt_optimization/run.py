"""Choose a prompt candidate using deterministic quality and cost criteria."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PromptCandidate:
    name: str
    text: str

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.text.strip():
            raise ValueError("Candidate name and text must be non-empty")


@dataclass(frozen=True, slots=True)
class OptimizationResult:
    winner: PromptCandidate
    scores: dict[str, float]


def select_best_prompt(
    candidates: Sequence[PromptCandidate], scorer: Callable[[str], float], *, length_penalty: float = 0.001
) -> OptimizationResult:
    """Maximize an explicit score while applying a small, predictable length penalty."""
    if not candidates or length_penalty < 0:
        raise ValueError("At least one candidate and a non-negative length penalty are required")
    scores: dict[str, float] = {}
    for candidate in candidates:
        quality = scorer(candidate.text)
        if not 0 <= quality <= 1:
            raise ValueError("scorer must return a value in [0, 1]")
        scores[candidate.name] = quality - length_penalty * len(candidate.text)
    winner = max(candidates, key=lambda candidate: (scores[candidate.name], candidate.name))
    return OptimizationResult(winner, scores)


def main() -> None:
    candidates = (
        PromptCandidate("concise", "Classify the sentiment: {review}"),
        PromptCandidate("specific", "Classify this review as positive or negative. Return one lowercase label: {review}"),
    )
    result = select_best_prompt(candidates, lambda prompt: 0.90 if "lowercase" in prompt else 0.82)
    print("result:", result)
    print(result.winner.name)


if __name__ == "__main__":
    main()
