from __future__ import annotations

import pytest

from applied_ai.reasoning import (
    critique,
    iterate,
    recover_execution,
    tool_reason,
    validate_python_syntax,
    verify_independently,
    verify_math,
    within_budget,
)


def test_bounded_reasoning_and_verification() -> None:
    assert iterate(0, lambda value: value + 1, max_steps=3, stop=lambda value: value == 2) == (2, 2)
    assert within_budget(2, 2)
    assert verify_math("6 * 7", 42)
    assert verify_independently("42", (str.isdigit,))
    assert critique("answer [source]", ("source", "number")) == ("number",)


def test_code_tools_and_recovery() -> None:
    assert validate_python_syntax("x = 1")
    assert not validate_python_syntax("x =")
    assert tool_reason("x", {"echo": lambda value: value}, "echo") == "x"
    assert (
        recover_execution(lambda: (_ for _ in ()).throw(RuntimeError()), lambda: "fallback")
        == "fallback"
    )
    with pytest.raises(ValueError):
        verify_math("__import__('os')", 1)
