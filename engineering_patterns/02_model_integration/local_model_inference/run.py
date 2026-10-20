"""Select a local Ollama provider explicitly, with an offline mock default."""

from __future__ import annotations

from applied_ai import LLMRequest, Message, MockProvider
from applied_ai.core.exceptions import ConfigurationError
from applied_ai.core.protocols import LLMProvider
from applied_ai.providers.ollama_provider import OllamaProvider


def create_local_provider(*, live: bool = False, base_url: str = "http://127.0.0.1:11434") -> LLMProvider:
    """Return a mock by default; a local server is contacted only with explicit opt-in."""
    if not live:
        return MockProvider(default_text="Local-model demonstration response")
    if not base_url.startswith(("http://", "https://")):
        raise ConfigurationError("Local provider URL must use HTTP(S)")
    return OllamaProvider(base_url=base_url)


def infer(provider: LLMProvider, model: str, prompt: str) -> str:
    if not prompt.strip():
        raise ValueError("prompt must be non-empty")
    return provider.generate(LLMRequest(model, (Message("user", prompt),))).text


def main() -> None:
    print(infer(create_local_provider(), "mock-local", "Give one local inference benefit."))


if __name__ == "__main__":
    main()
