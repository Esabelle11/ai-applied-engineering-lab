"""Use the common provider contract rather than provider-specific application code."""

from __future__ import annotations

from applied_ai import LLMRequest, LLMResponse, Message
from applied_ai.core.protocols import LLMProvider
from applied_ai.providers import ProviderRegistry


def generate_reply(provider: LLMProvider, model: str, question: str) -> LLMResponse:
    """Application code depends only on the provider-neutral protocol."""
    if not question.strip():
        raise ValueError("question must be non-empty")
    return provider.generate(LLMRequest(model, (Message("user", question),)))


def create_registry() -> ProviderRegistry:
    """Register provider builders at composition time rather than in application logic."""
    from applied_ai import MockProvider

    registry = ProviderRegistry()
    registry.register("concise", lambda: MockProvider(default_text="Concise answer"))
    registry.register("detailed", lambda: MockProvider(default_text="Detailed answer"))
    return registry


def main() -> None:
    registry = create_registry()
    print(generate_reply(registry.create("concise"), "mock", "Explain RAG").text)


if __name__ == "__main__":
    main()
