from __future__ import annotations

import pytest

from applied_ai import LLMResponse
from applied_ai.execution import KernelExecutionResult
from case_studies.loop_tool_agent.agent import decode_action, run_agent_attempt
from case_studies.loop_tool_agent.data import MathQuestion, load_questions, select_questions


def test_math_dataset_loads_and_sample_is_reproducible() -> None:
    questions = load_questions()
    assert len(questions) == 50
    assert select_questions(questions, count=2, seed=7) == select_questions(
        questions, count=2, seed=7
    )


def test_action_decoder_accepts_only_supported_json_actions() -> None:
    assert decode_action('{"action":"answer","answer":42}') == ("answer", "42")
    assert decode_action('{"action":"python","code":"print(42)"}') == (
        "python",
        "print(42)",
    )
    assert decode_action("The answer is 42") is None


def test_sample_validation_rejects_invalid_count() -> None:
    with pytest.raises(ValueError):
        select_questions((MathQuestion(1, "x", "1"),), count=2, seed=1)


def test_agent_executes_python_then_returns_final_answer() -> None:
    class FakeProvider:
        def __init__(self) -> None:
            self.responses = iter(
                (
                    '{"action":"python","code":"print(6 * 7)"}',
                    '{"action":"answer","answer":42}',
                )
            )

        def generate(self, _request):
            return LLMResponse(next(self.responses), "model", "fake")

    class FakeExecutor:
        def execute(
            self, source: str, *, timeout_seconds: float | None = None
        ) -> KernelExecutionResult:
            assert source == "print(6 * 7)"
            assert timeout_seconds == 8.0
            return KernelExecutionResult("42\n")

    result = run_agent_attempt(
        FakeProvider(),
        "model",
        MathQuestion(1, "Calculate", "42"),
        FakeExecutor(),
        max_turns=3,
        max_output_tokens=128,
    )
    assert result.answer == "42"
    assert result.tool_calls == 1
    assert result.turns == 2
