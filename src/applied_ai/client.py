"""Small high-level client over the provider-neutral contracts."""

from __future__ import annotations

from collections.abc import Sequence

from applied_ai.core import LLMRequest, LLMResponse, Message
from applied_ai.providers.factory import ProviderFactory
from applied_ai.core.protocols import LLMProvider


class AppliedAIClient:
    def __init__(self, provider: LLMProvider, model: str) -> None:
        if not model.strip():
            raise ValueError("model must be non-empty")
        self.provider = provider
        self.model = model

    @classmethod
    def from_environment(cls, *, allow_live: bool = False) -> "AppliedAIClient":
        selection = ProviderFactory().create(allow_live=allow_live)
        return cls(selection.provider, selection.model)

    def generate(self, messages: Sequence[Message], **options: object) -> LLMResponse:
        request = LLMRequest(self.model, tuple(messages), **options)  # type: ignore[arg-type]
        return self.provider.generate(request)

    def ask(self, prompt: str, **options: object) -> LLMResponse:
        return self.generate((Message("user", prompt),), **options)
