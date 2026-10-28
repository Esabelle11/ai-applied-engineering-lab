"""Dataset loading and reproducible sampling for the loop-tool case study."""

from __future__ import annotations

import csv
import random
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

DATASET = Path(__file__).with_name("data") / "50problems.csv"


@dataclass(frozen=True, slots=True)
class MathQuestion:
    """One math problem and its known integer answer."""

    index: int
    problem: str
    expected: str


def load_questions(path: Path = DATASET) -> tuple[MathQuestion, ...]:
    """Load the CSV and fail early if it is not the expected teaching dataset."""
    with path.open(encoding="utf-8", newline="") as handle:
        rows = tuple(csv.DictReader(handle))
    if not rows or not {"Problem", "Answer"}.issubset(rows[0]):
        raise ValueError("Dataset must be a non-empty CSV with Problem and Answer columns")
    questions = tuple(
        MathQuestion(index, row["Problem"].strip(), row["Answer"].strip())
        for index, row in enumerate(rows, 1)
    )
    if any(not question.problem or not question.expected for question in questions):
        raise ValueError("Every dataset row needs a Problem and Answer")
    return questions


def select_questions(
    questions: Sequence[MathQuestion], *, count: int, seed: int
) -> tuple[MathQuestion, ...]:
    """Choose a stable small sample, rather than accidentally running all 50 rows."""
    if not 1 <= count <= len(questions):
        raise ValueError("count must be between 1 and the dataset size")
    return tuple(random.Random(seed).sample(list(questions), count))
