"""Opt-in provider factory: one environment configuration, all case studies.

No API keys are printed. Environment takes precedence over .env. Mock is default.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from applied_ai.core.exceptions import ConfigurationError
from applied_ai.core.protocols import LLMProvider
from applied_ai.providers.mock import MockProvider

SUPPORTED_PROVIDERS = frozenset({"mock", "openai", "openrouter", "anthropic", "google", "ollama"})
DEFAULT_MODELS = {
    "mock": "mock-model",
    "openrouter": "nvidia/nemotron-3.5-lightning:free",
    "openai": "gpt-4.1-mini",
    "anthropic": "claude-haiku-4-5",
    "google": "gemini-3.5-flash",
    "ollama": "llama3.2",
}


def read_dotenv(path: Path | str = ".env") -> dict[str, str]:
    """Read a minimal KEY=VALUE file without command execution or global mutation."""
    path = Path(path)
    if not path.is_file():
        return {}
    result: dict[str, str] = {}
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            raise ConfigurationError(f"Invalid .env syntax on line {lineno}")
        key, value = line.split("=", 1)
        key = key.strip()
        if not key.isidentifier() or not key.isascii():
            raise ConfigurationError(f"Invalid .env variable on line {lineno}")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        result[key] = value
    return result


@dataclass(frozen=True, slots=True)
class ProviderSelection:
    provider: LLMProvider
    model: str


class ProviderFactory:
    def __init__(
        self, *, env: Mapping[str, str] | None = None, dotenv: Path | str = ".env"
    ) -> None:
        self.env = {**read_dotenv(dotenv), **dict(os.environ if env is None else env)}
        self.kind = self.env.get("AI_LAB_PROVIDER", "mock").strip().lower() or "mock"
        if self.kind not in SUPPORTED_PROVIDERS:
            raise ConfigurationError(
                f"Unsupported provider {self.kind!r}; choices: {', '.join(sorted(SUPPORTED_PROVIDERS))}"
            )
        self.model = self.env.get("AI_LAB_MODEL", "").strip() or DEFAULT_MODELS[self.kind]
        try:
            self.timeout = float(self.env.get("APP_REQUEST_TIMEOUT_SECONDS", "30"))
        except ValueError as exc:
            raise ConfigurationError("APP_REQUEST_TIMEOUT_SECONDS must be numeric") from exc
        if not 0 < self.timeout <= 600:
            raise ConfigurationError("APP_REQUEST_TIMEOUT_SECONDS must be in (0,600]")

    def create(
        self, *, allow_live: bool = False, mock_text: str = "Mock response"
    ) -> ProviderSelection:
        """Refuse unintended network calls even if .env selects a live provider."""
        kind = self.kind
        if kind != "mock" and not allow_live:
            raise ConfigurationError("Live provider selected: pass --live to authorize API access")
        if kind == "mock":
            return ProviderSelection(MockProvider(default_text=mock_text), self.model)
        if kind == "openai":
            from applied_ai.providers.openai_provider import OpenAIProvider

            provider: LLMProvider = OpenAIProvider(
                api_key=self.env.get("OPENAI_API_KEY"), timeout_seconds=self.timeout
            )
        elif kind == "openrouter":
            from applied_ai.providers.openrouter_provider import OpenRouterProvider

            provider = OpenRouterProvider(
                api_key=self.env.get("OPENROUTER_API_KEY"), timeout_seconds=self.timeout
            )
        elif kind == "anthropic":
            from applied_ai.providers.anthropic_provider import AnthropicProvider

            provider = AnthropicProvider(
                api_key=self.env.get("ANTHROPIC_API_KEY"), timeout_seconds=self.timeout
            )
        elif kind == "google":
            from applied_ai.providers.google_provider import GoogleProvider

            provider = GoogleProvider(
                api_key=self.env.get("GOOGLE_API_KEY") or self.env.get("GEMINI_API_KEY"),
                timeout_seconds=self.timeout,
            )
        else:
            from applied_ai.providers.ollama_provider import OllamaProvider

            provider = OllamaProvider(
                base_url=self.env.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
                timeout_seconds=self.timeout,
            )
        return ProviderSelection(provider, self.model)
