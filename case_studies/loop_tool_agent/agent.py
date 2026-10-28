"""The teachable LLM -> Python -> feedback -> answer loop.

The shared provider interface is text-only, so the model communicates tool
actions through a deliberately small JSON protocol. This makes the example
work with Groq, OpenRouter, OpenAI, and the other lab providers.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Protocol

from applied_ai import LLMRequest, LLMResponse, Message
from applied_ai.execution import KernelExecutionResult
from case_studies.loop_tool_agent.data import MathQuestion

MAX_TOOL_SOURCE_CHARS = 8_000


class Provider(Protocol):
    def generate(self, request: LLMRequest) -> LLMResponse: ...


class Executor(Protocol):
    def execute(
        self, source: str, *, timeout_seconds: float | None = None
    ) -> KernelExecutionResult: ...


@dataclass(frozen=True, slots=True)
class AgentAttempt:
    """Trace summary for one independent solution path."""

    answer: str | None
    turns: int
    tool_calls: int
    errors: tuple[str, ...]
    termination_reason: str


def decode_action(text: str) -> tuple[str, str] | None:
    """Accept only the two JSON actions defined by this example's protocol."""
    candidates = [text.strip()]
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", text.strip(), flags=re.DOTALL)
    if fenced:
        candidates.append(fenced.group(1))
    for candidate in candidates:
        try:
            value = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if not isinstance(value, dict):
            continue
        action = value.get("action")
        if action == "python" and isinstance(value.get("code"), str):
            return "python", value["code"]
        if action == "answer" and isinstance(value.get("answer"), (str, int)):
            answer = str(value["answer"]).strip()
            if re.fullmatch(r"[+-]?\d+", answer):
                return "answer", answer
    return None


def _tool_result(result: KernelExecutionResult) -> str:
    """Bound the feedback returned to the LLM, including failures."""
    if result.timed_out:
        return f"[PYTHON ERROR] {result.error or 'execution timed out'}"
    if result.error:
        return f"[PYTHON ERROR]\n{result.error[-4_000:]}"
    return f"[PYTHON OUTPUT]\n{result.stdout[-4_000:]}"


def _system_prompt() -> str:
    return """You solve one mathematics problem using a Python verification tool.
Before giving an answer, make at least one Python tool call to verify a calculation.
Reply with exactly one JSON object and no Markdown:
{"action":"python","code":"Python source that prints its result"}
or, after reading the tool result:
{"action":"answer","answer":123}
The final answer must be an integer. Do not include any other fields or prose."""


def run_agent_attempt(
    provider: Provider,
    model: str,
    question: MathQuestion,
    executor: Executor,
    *,
    max_turns: int,
    max_output_tokens: int,
    tool_timeout_seconds: float = 8.0,
) -> AgentAttempt:
    """Solve one question, requiring a Python verification before the answer."""
    messages = [Message("system", _system_prompt()), Message("user", question.problem)]
    errors: list[str] = []
    tool_calls = 0
    for turn in range(1, max_turns + 1):
        response = provider.generate(
            LLMRequest(
                model,
                tuple(messages),
                max_output_tokens=max_output_tokens,
                temperature=0,
                reasoning_effort="low",
            )
        )
        decoded = decode_action(response.text)
        if decoded is None:
            errors.append("Model response was not a supported JSON tool action")
            messages.append(
                Message(
                    "user",
                    "Your previous response was invalid. Reply only with the required JSON action object.",
                )
            )
            continue
        action, payload = decoded
        messages.append(Message("assistant", response.text))
        if action == "answer":
            if tool_calls == 0:
                errors.append("Model attempted an answer before Python verification")
                messages.append(
                    Message("user", "Use the Python tool once before submitting the final answer."),
                )
                continue
            return AgentAttempt(payload, turn, tool_calls, tuple(errors), "answer")
        if tool_calls >= 1:
            errors.append("Python tool-call budget exhausted")
            messages.append(
                Message("user", "Use the previous tool output and submit the final answer now.")
            )
            continue
        if not payload.strip() or len(payload) > MAX_TOOL_SOURCE_CHARS:
            errors.append("Python source was empty or exceeded the 8 KiB limit")
            messages.append(
                Message("user", "Submit shorter Python code or an answer after verification.")
            )
            continue
        tool_calls += 1
        result = executor.execute(payload, timeout_seconds=tool_timeout_seconds)
        messages.append(Message("user", _tool_result(result)))
    return AgentAttempt(None, max_turns, tool_calls, tuple(errors), "turn_budget")
