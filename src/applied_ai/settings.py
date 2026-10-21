"""Validated runtime settings loaded from environment mappings."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass

from applied_ai.core.exceptions import ConfigurationError


@dataclass(frozen=True, slots=True)
class Settings:
    provider: str = "mock"
    model: str = "mock-model"
    request_timeout_seconds: float = 30.0
    max_retries: int = 2
    allow_live: bool = False

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> Settings:
        values = dict(os.environ if env is None else env)
        try:
            timeout = float(values.get("APP_REQUEST_TIMEOUT_SECONDS", "30"))
            retries = int(values.get("AI_LAB_MAX_RETRIES", "2"))
        except ValueError as exc:
            raise ConfigurationError("Timeout and retry settings must be numeric") from exc
        provider = values.get("AI_LAB_PROVIDER", "mock").strip().lower() or "mock"
        model = values.get("AI_LAB_MODEL", "").strip() or (
            "mock-model" if provider == "mock" else ""
        )
        if not model:
            raise ConfigurationError("AI_LAB_MODEL is required for live providers")
        if not 0 < timeout <= 600 or retries < 0 or retries > 20:
            raise ConfigurationError("Runtime settings are outside safe bounds")
        allow_live = values.get("AI_LAB_ALLOW_LIVE", "false").lower() in {"1", "true", "yes"}
        return cls(provider, model, timeout, retries, allow_live)
