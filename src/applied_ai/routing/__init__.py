"""Explicit provider-neutral selection of provider and model IDs."""

from __future__ import annotations

from dataclasses import dataclass, replace

from applied_ai.core.exceptions import CapabilityNotSupportedError
from applied_ai.core.protocols import LLMProvider
from applied_ai.core.requests import LLMRequest
from applied_ai.core.responses import LLMResponse


@dataclass(frozen=True, slots=True)
class ModelTarget:
    provider: LLMProvider
    model: str

    def __post_init__(self) -> None:
        if not self.model.strip():
            raise ValueError("Model target requires a model identifier")


class TaskRouter:
    """Caller selects a named task; no heuristic or silent provider substitution."""

    def __init__(self, targets: dict[str, ModelTarget]) -> None:
        if not targets or any(not task.strip() for task in targets):
            raise ValueError("Supply at least one non-empty task name")
        self._targets = dict(targets)

    def generate(self, task: str, request: LLMRequest) -> LLMResponse:
        if task not in self._targets:
            raise ValueError(f"Unconfigured route: {task}")
        target = self._targets[task]
        # print("request:", request)
        if request.response_format and not target.provider.capabilities.structured_output:
            raise CapabilityNotSupportedError(
                "Selected provider does not support structured output",
                provider=target.provider.name,
            )
        return target.provider.generate(replace(request, model=target.model))
