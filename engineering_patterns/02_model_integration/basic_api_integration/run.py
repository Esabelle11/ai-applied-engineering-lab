"""Run the exact same LLMRequest against a mock or a live OpenAI backend."""

from __future__ import annotations

import argparse

from applied_ai import LLMRequest, Message, MockProvider
from applied_ai.core.protocols import LLMProvider

QUESTION = "Explain retrieval-augmented generation in one sentence."


def create_provider(kind: str) -> LLMProvider:
    if kind == "mock":
        return MockProvider(
            responses={QUESTION: "RAG grounds a model's answer in retrieved documents."}
        )
    if kind == "openai":
        from applied_ai.providers.openai_provider import OpenAIProvider

        return OpenAIProvider()
    raise ValueError(f"Unsupported provider: {kind}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 1 provider-neutral demonstration")
    parser.add_argument("--provider", choices=["mock", "openai"], default="mock")
    parser.add_argument("--model", default=None, help="Model ID used by the selected provider")
    arguments = parser.parse_args()
    model = arguments.model or ("mock-model" if arguments.provider == "mock" else "gpt-4.1-mini")
    request = LLMRequest(model=model, messages=(Message(role="user", content=QUESTION),))
    provider = create_provider(arguments.provider)
    try:
        result = provider.generate(request)
    finally:
        close = getattr(provider, "close", None)
        if callable(close):
            close()
    print(f"Provider: {result.provider} | Model: {result.model}")
    print(f"Response: {result.text}")
    print(f"Usage: {result.usage} | Latency: {result.latency_seconds}s")


if __name__ == "__main__":
    main()
