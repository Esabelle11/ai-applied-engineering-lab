"""Bounded model-to-tool feedback loops with explicit failure handling."""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class ToolCall:
    name: str
    arguments: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class ModelTurn:
    text: str = ""
    tool_calls: tuple[ToolCall, ...] = ()


@dataclass(frozen=True, slots=True)
class LoopMessage:
    role: str
    content: str


class Model(Protocol):
    def __call__(self, messages: tuple[LoopMessage, ...]) -> ModelTurn: ...


Tool = Callable[[Mapping[str, Any]], str]


@dataclass(frozen=True, slots=True)
class ToolLoopResult:
    answer: str | None
    turns: int
    tool_calls: int
    errors: tuple[str, ...]
    termination_reason: str


class ToolLoop:
    def __init__(
        self,
        model: Model,
        tools: Mapping[str, Tool],
        *,
        max_turns: int = 5,
        max_tool_calls: int = 8,
        deadline_seconds: float = 30.0,
    ) -> None:
        if max_turns < 1 or max_tool_calls < 1 or deadline_seconds <= 0:
            raise ValueError("Loop limits must be positive")
        self.model = model
        self.tools = dict(tools)
        self.max_turns = max_turns
        self.max_tool_calls = max_tool_calls
        self.deadline_seconds = deadline_seconds

    def run(self, prompt: str) -> ToolLoopResult:
        if not prompt.strip():
            raise ValueError("prompt must be non-empty")
        messages = [LoopMessage("user", prompt)]
        errors: list[str] = []
        calls = 0
        started = time.monotonic()
        for turn in range(1, self.max_turns + 1):
            if time.monotonic() - started >= self.deadline_seconds:
                return ToolLoopResult(None, turn - 1, calls, tuple(errors), "deadline")
            response = self.model(tuple(messages))
            if not response.tool_calls:
                return ToolLoopResult(
                    response.text.strip() or None, turn, calls, tuple(errors), "answer"
                )
            messages.append(LoopMessage("assistant", response.text))
            for call in response.tool_calls:
                calls += 1
                if calls > self.max_tool_calls:
                    return ToolLoopResult(None, turn, calls - 1, tuple(errors), "tool_budget")
                tool = self.tools.get(call.name)
                if tool is None:
                    error = f"Unknown tool: {call.name}"
                    errors.append(error)
                    messages.append(LoopMessage("tool", f"[ERROR] {error}"))
                    continue
                try:
                    result = tool(call.arguments)
                except Exception as exc:  # tool errors become model-visible feedback
                    error = f"{type(exc).__name__}: {exc}"
                    errors.append(error)
                    result = f"[ERROR] {error}"
                messages.append(LoopMessage("tool", result))
        return ToolLoopResult(None, self.max_turns, calls, tuple(errors), "turn_budget")
