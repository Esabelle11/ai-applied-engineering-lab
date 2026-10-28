"""Bounded propose-and-verify loop; never evaluates or executes generated code."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from applied_ai.core.messages import Message
from applied_ai.core.protocols import LLMProvider
from applied_ai.core.requests import LLMRequest
from applied_ai.reasoning.consensus import (
    ConsensusResult,
    majority_consensus,
)
from applied_ai.reasoning.primitives import (
    critique,
    iterate,
    recover_execution,
    tool_reason,
    validate_python_syntax,
    verify_independently,
    verify_math,
    within_budget,
)
from applied_ai.reasoning.tool_loop import (
    LoopMessage,
    ModelTurn,
    ToolCall,
    ToolLoop,
    ToolLoopResult,
)

__all__ = [
    "ConsensusResult",
    "LoopMessage",
    "ModelTurn",
    "ToolCall",
    "ToolLoop",
    "ToolLoopResult",
    "VerificationLoop",
    "VerificationResult",
    "critique",
    "iterate",
    "majority_consensus",
    "recover_execution",
    "tool_reason",
    "validate_python_syntax",
    "verify_independently",
    "verify_math",
    "within_budget",
]


@dataclass(frozen=True, slots=True)
class VerificationResult:
    answer: str
    accepted: bool
    attempts: int


class VerificationLoop:
    def __init__(self, provider: LLMProvider, model: str, *, max_attempts: int = 3) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be positive")
        self.provider = provider
        self.model = model
        self.max_attempts = max_attempts

    def solve(self, question: str, verifier: Callable[[str], bool]) -> VerificationResult:
        feedback = ""
        for attempt in range(1, self.max_attempts + 1):
            prompt = question if not feedback else f"{question}\n{feedback}"
            answer = self.provider.generate(LLMRequest(self.model, (Message("user", prompt),))).text
            if verifier(answer):
                return VerificationResult(answer, True, attempt)
            feedback = "Previous answer failed independent verification. Try again."
        return VerificationResult(answer, False, self.max_attempts)
