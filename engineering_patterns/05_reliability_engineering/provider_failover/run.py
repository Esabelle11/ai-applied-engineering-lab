"""Fail over from a transiently failing provider to a named fallback."""

from applied_ai import LLMRequest, Message, MockProvider
from applied_ai.core.capabilities import ProviderCapabilities
from applied_ai.core.exceptions import ProviderUnavailableError
from applied_ai.core.protocols import LLMProvider
from applied_ai.core.responses import LLMResponse
from applied_ai.reliability import ReliableProvider, RetryPolicy


class NamedProvider:
    def __init__(self, name: str, delegate: LLMProvider) -> None:
        self._name = name
        self._delegate = delegate

    @property
    def name(self) -> str:
        return self._name

    @property
    def capabilities(self) -> ProviderCapabilities:
        return self._delegate.capabilities

    def generate(self, request: LLMRequest) -> LLMResponse:
        return self._delegate.generate(request)


def main() -> None:
    primary = NamedProvider("primary", MockProvider(faults=(ProviderUnavailableError("outage"),)))
    fallback = NamedProvider("fallback", MockProvider(default_text="fallback answer"))
    provider = ReliableProvider(primary, fallbacks=(fallback,), policy=RetryPolicy(max_attempts=1))
    print(provider.generate(LLMRequest("mock", (Message("user", "hello"),))).text)


if __name__ == "__main__":
    main()
