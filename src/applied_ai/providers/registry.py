"""Explicit provider registry for dependency-injection and tests."""

from __future__ import annotations

from collections.abc import Callable

from applied_ai.core.exceptions import ConfigurationError
from applied_ai.core.protocols import LLMProvider

ProviderBuilder = Callable[[], LLMProvider]


class ProviderRegistry:
    """Map stable names to provider builders without hidden global state."""

    def __init__(self) -> None:
        self._builders: dict[str, ProviderBuilder] = {}

    def register(self, name: str, builder: ProviderBuilder, *, replace: bool = False) -> None:
        if not name.strip() or not callable(builder):
            raise ValueError("Provider name and callable builder are required")
        if name in self._builders and not replace:
            raise ConfigurationError(f"Provider already registered: {name}")
        self._builders[name] = builder

    def create(self, name: str) -> LLMProvider:
        try:
            provider = self._builders[name]()
        except KeyError as exc:
            raise ConfigurationError(f"Unknown provider: {name}") from exc
        if not isinstance(provider, LLMProvider):
            raise TypeError("Provider builder did not return an LLMProvider")
        return provider

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._builders))
