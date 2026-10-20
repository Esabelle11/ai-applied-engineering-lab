"""Bounded, deterministic reasoning helpers; never execute generated code in-process."""

from __future__ import annotations

import ast
from collections.abc import Callable, Mapping, Sequence


def iterate[T](
    initial: T, step: Callable[[T], T], *, max_steps: int, stop: Callable[[T], bool]
) -> tuple[T, int]:
    if max_steps < 1:
        raise ValueError("max_steps must be positive")
    current = initial
    for attempt in range(1, max_steps + 1):
        current = step(current)
        if stop(current):
            return current, attempt
    return current, max_steps


def within_budget(used: int, limit: int) -> bool:
    if used < 0 or limit < 0:
        raise ValueError("Budgets cannot be negative")
    return used <= limit


def verify_math(expression: str, expected: int | float) -> bool:
    tree = ast.parse(expression, mode="eval")
    if not all(
        isinstance(
            node,
            (
                ast.Expression,
                ast.BinOp,
                ast.Add,
                ast.Sub,
                ast.Mult,
                ast.Div,
                ast.Constant,
                ast.USub,
                ast.UnaryOp,
            ),
        )
        for node in ast.walk(tree)
    ):
        raise ValueError("Only basic arithmetic is allowed")
    return eval(compile(tree, "<math>", "eval"), {"__builtins__": {}}, {}) == expected  # noqa: S307


def verify_independently(answer: str, checks: Sequence[Callable[[str], bool]]) -> bool:
    return bool(checks) and all(check(answer) for check in checks)


def critique(answer: str, requirements: Sequence[str]) -> tuple[str, ...]:
    return tuple(
        requirement for requirement in requirements if requirement.lower() not in answer.lower()
    )


def validate_python_syntax(code: str) -> bool:
    try:
        ast.parse(code, mode="exec")
    except SyntaxError:
        return False
    return True


def tool_reason(query: str, tools: Mapping[str, Callable[[str], str]], tool_name: str) -> str:
    if tool_name not in tools or not query.strip():
        raise ValueError("Known tool and query are required")
    return tools[tool_name](query)


def recover_execution[T](operation: Callable[[], T], fallback: Callable[[], T]) -> T:
    try:
        return operation()
    except (RuntimeError, ValueError):
        return fallback()
