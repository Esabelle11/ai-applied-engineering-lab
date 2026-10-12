"""Single synchronous provider protocol for the Phase 1 vertical slice."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from applied_ai.core.capabilities import ProviderCapabilities
from applied_ai.core.requests import LLMRequest
from applied_ai.core.responses import LLMResponse


@runtime_checkable
class LLMProvider(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def capabilities(self) -> ProviderCapabilities: ...

    def generate(self, request: LLMRequest) -> LLMResponse: ...
