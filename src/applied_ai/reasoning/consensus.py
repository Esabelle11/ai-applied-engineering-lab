"""Deterministic consensus for independent agent attempts."""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class ConsensusResult[T]:
    answer: T | None
    votes: int
    total_answers: int
    early_stopped: bool


def majority_consensus[T](
    answers: Sequence[T | None], *, early_stop_votes: int | None = None
) -> ConsensusResult[T]:
    valid = [answer for answer in answers if answer is not None]
    if not valid:
        return ConsensusResult(None, 0, 0, False)
    counts = Counter(valid)
    first_seen = {answer: index for index, answer in enumerate(valid)}
    winner = max(counts, key=lambda answer: (counts[answer], -first_seen[answer]))
    return ConsensusResult(
        winner,
        counts[winner],
        len(valid),
        early_stop_votes is not None and counts[winner] >= early_stop_votes,
    )
