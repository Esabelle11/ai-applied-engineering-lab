"""Offline deterministic provider with scripted response mapping and fault injection."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from applied_ai.core.capabilities import ProviderCapabilities
from applied_ai.core.exceptions import CapabilityNotSupportedError, LLMError
from applied_ai.core.requests import LLMRequest
from applied_ai.core.responses import LLMResponse, TokenUsage
from applied_ai.core.structured import parse_structured_output


class MockProvider:
    """Return fixed responses and raise scripted errors in call order, without network access."""

    def __init__(
        self,
        *,
        default_text: str = "Mock response",
        responses: Mapping[str, str] | None = None,
        faults: Sequence[LLMError] = (),
        usage: TokenUsage | None = None,
        supports_structured_output: bool = True,
    ) -> None:
        self._default_text = default_text
        self._responses = dict(responses or {})
        self._faults = tuple(faults)
        self._usage = usage
        self._capabilities = ProviderCapabilities(structured_output=supports_structured_output)
        self.call_count = 0

    @property
    def name(self) -> str:
        return "mock"

    @property
    def capabilities(self) -> ProviderCapabilities:
        return self._capabilities

    def generate(self, request: LLMRequest) -> LLMResponse:
        if request.response_format is not None and not self.capabilities.structured_output:
            raise CapabilityNotSupportedError(
                "Mock provider does not support structured output", provider=self.name
            )
        self.call_count += 1
        if self.call_count <= len(self._faults):
            raise self._faults[self.call_count - 1]
        last_user = next(
            (item.content for item in reversed(request.messages) if item.role == "user"),
            request.messages[-1].content,
        )
        content = self._responses.get(last_user, self._default_text)
        parsed = (
            parse_structured_output(content, request.response_format, provider=self.name)
            if request.response_format is not None
            else None
        )
        return LLMResponse(
            text=content,
            model=request.model,
            provider=self.name,
            request_id=f"mock-{self.call_count:04d}",
            finish_reason="completed",
            usage=self._usage,
            latency_seconds=0.0,
            parsed_output=parsed,
        )
