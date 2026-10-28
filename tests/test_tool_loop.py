from __future__ import annotations

from applied_ai.reasoning import ModelTurn, ToolCall, ToolLoop, majority_consensus


def test_tool_loop_provides_execution_feedback() -> None:
    calls = 0

    def model(messages):
        nonlocal calls
        calls += 1
        if calls == 1:
            return ModelTurn(tool_calls=(ToolCall("calculate", {"value": 6}),))
        assert messages[-1].role == "tool"
        return ModelTurn("The verified answer is 42.")

    result = ToolLoop(model, {"calculate": lambda args: str(args["value"] * 7)}).run("Solve")
    assert result.answer == "The verified answer is 42."
    assert result.turns == 2
    assert result.tool_calls == 1
    assert result.termination_reason == "answer"


def test_tool_loop_turns_errors_into_feedback() -> None:
    def model(messages):
        if len(messages) == 1:
            return ModelTurn(tool_calls=(ToolCall("missing", {}),))
        return ModelTurn("I corrected the plan.")

    result = ToolLoop(model, {}).run("Solve")
    assert result.answer == "I corrected the plan."
    assert result.errors == ("Unknown tool: missing",)


def test_consensus_is_deterministic_and_can_report_early_stop() -> None:
    result = majority_consensus(("a", "b", "a"), early_stop_votes=2)
    assert result.answer == "a"
    assert result.votes == 2
    assert result.early_stopped
