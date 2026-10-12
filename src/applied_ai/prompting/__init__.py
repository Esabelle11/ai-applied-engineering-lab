"""Strict variable templates and sequential provider-backed prompt composition."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from applied_ai.core.messages import Message
from applied_ai.core.protocols import LLMProvider
from applied_ai.core.requests import LLMRequest

_FIELD = re.compile(r"\{([a-z][a-z0-9_]*)\}")
_BAD_FIELD = re.compile(r"\{[^{}]*\}")


@dataclass(frozen=True, slots=True)
class PromptTemplate:
    template: str

    def render(self, values: Mapping[str, str]) -> str:
        fields = set(_FIELD.findall(self.template))
        remaining = _FIELD.sub("", self.template)
        if _BAD_FIELD.search(remaining) or "{" in remaining or "}" in remaining:
            raise ValueError("Only simple placeholders like {topic} are supported")
        missing = fields - values.keys()
        if missing:
            raise ValueError(f"Missing prompt variables: {', '.join(sorted(missing))}")
        if any(not isinstance(values[key], str) for key in fields):
            raise TypeError("Prompt variables must be text")
        return _FIELD.sub(lambda match: values[match.group(1)], self.template)


@dataclass(frozen=True, slots=True)
class PromptStep:
    name: str
    template: PromptTemplate


class PromptChain:
    def __init__(self, steps: Sequence[PromptStep]) -> None:
        if not steps or len({step.name for step in steps}) != len(steps):
            raise ValueError("Steps must be present and names unique")
        if any(not re.fullmatch(r"[a-z][a-z0-9_]*", step.name) for step in steps):
            raise ValueError("Invalid step name")
        self.steps = tuple(steps)

    def run(
        self, provider: LLMProvider, model: str, variables: Mapping[str, str]
    ) -> dict[str, str]:
        context = dict(variables)
        for step in self.steps:
            if step.name in context:
                raise ValueError(f"Step would overwrite existing value: {step.name}")
            prompt = step.template.render(context)
            response = provider.generate(LLMRequest(model, (Message("user", prompt),)))
            context[step.name] = response.text
        return context
