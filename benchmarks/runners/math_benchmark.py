"""Mock model strategies with actual safe arithmetic tool (not Python sandbox)."""

from __future__ import annotations

import ast
import json
from pathlib import Path

from applied_ai.core import LLMRequest, Message, TokenUsage
from applied_ai.experimentation import ExperimentManifest, Observation
from applied_ai.providers.mock import MockProvider
from applied_ai.reasoning import VerificationLoop


class UnsupportedExpression(ValueError):
    """Only bounded integer arithmetic expressions are supported."""


def arithmetic(expression: str) -> int:
    """Interpret a tiny, safe integer AST. No eval, exec, imports or Python calls."""
    if len(expression) > 100:
        raise UnsupportedExpression("Expression too long")
    try:
        root = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise UnsupportedExpression("Invalid syntax") from exc
    if sum(1 for _ in ast.walk(root)) > 31:
        raise UnsupportedExpression("Expression too complex")

    def visit(node: ast.AST) -> int:
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if (
            isinstance(node, ast.Constant)
            and type(node.value) is int
            and abs(node.value) <= 1_000_000
        ):
            return node.value
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            result = visit(node.operand)
            return -result if isinstance(node.op, ast.USub) else result
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult)):
            left, right = visit(node.left), visit(node.right)
            value = (
                left + right
                if isinstance(node.op, ast.Add)
                else (left - right if isinstance(node.op, ast.Sub) else left * right)
            )
            if abs(value) > 1_000_000_000:
                raise UnsupportedExpression("Result exceeds safe bound")
            return value
        raise UnsupportedExpression("Only bounded integer +, -, * and parentheses permitted")

    return visit(root)


def parsed_int(answer: str) -> int | None:
    try:
        return int(answer.strip()) if answer.strip().lstrip("+-").isdigit() else None
    except ValueError:
        return None


def run(spec: ExperimentManifest, dataset: Path) -> list[Observation]:
    cases = json.loads(dataset.read_text(encoding="utf-8"))
    if set(spec.implementations) != {"direct", "arithmetic_tool", "verification_loop"}:
        raise ValueError("Math manifest strategies mismatch")
    for case in cases:
        if arithmetic(case["expression"]) != int(case["expected"]):
            raise ValueError("Dataset mathematical oracle mismatch")
    rows: list[Observation] = []
    usage = TokenUsage(input_tokens=8, output_tokens=4, total_tokens=12)
    for repeat in range(spec.repetitions):
        for case in cases:
            expected = int(case["expected"])
            for name in spec.implementations:
                model_calls = 1
                tool_success = None
                category = None
                if name == "direct":
                    provider = MockProvider(default_text=case["direct_answer"], usage=usage)
                    answer = provider.generate(
                        LLMRequest("mock", (Message("user", case["question"]),))
                    ).text
                    correct = parsed_int(answer) == expected
                    latency = 0.020
                elif name == "arithmetic_tool":
                    provider = MockProvider(default_text=case["tool_expression"], usage=usage)
                    proposal = provider.generate(
                        LLMRequest("mock", (Message("user", case["question"]),))
                    ).text
                    try:
                        answer = str(arithmetic(proposal))
                        correct = parsed_int(answer) == expected
                        tool_success = True
                    except UnsupportedExpression:
                        correct = False
                        tool_success = False
                        category = "invalid_tool_expression"
                    latency = 0.024
                else:
                    text = "Previous answer failed independent verification. Try again."
                    mapping = {
                        case["question"]: case["direct_answer"],
                        f"{case['question']}\n{text}": case["corrected_answer"],
                    }
                    provider = MockProvider(responses=mapping, usage=usage)
                    # result = VerificationLoop(provider, "mock", max_attempts=2).solve(
                    #     case["question"], lambda answer: parsed_int(answer) == expected,
                    # )
                    result = VerificationLoop(provider, "mock", max_attempts=2).solve(
                        case["question"],
                        lambda answer, expected=expected: parsed_int(answer) == expected,
                    )
                    model_calls = provider.call_count
                    correct = result.accepted
                    latency = model_calls * 0.020 + model_calls * 0.003
                rows.append(
                    Observation(
                        spec.id,
                        case["id"],
                        name,
                        repeat,
                        "error" if category else "completed",
                        correct,
                        latency,
                        "simulated",
                        attempts=model_calls,
                        tool_success=tool_success,
                        input_tokens=8 * model_calls,
                        output_tokens=4 * model_calls,
                        usage_kind="fixture",
                        error_category=category,
                        note="Synthetic model fixtures; arithmetic tool uses restricted AST (NOT Docker)",
                    )
                )
    return rows
