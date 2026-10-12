"""Dependency-free, non-secret runtime configuration for the foundation phase."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RuntimeConfig:
    """Validated non-secret settings. No .env or API keys are loaded here."""

    environment: str = "development"
    log_level: str = "INFO"
    request_timeout_seconds: float = 30.0
    max_retries: int = 3

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> RuntimeConfig:
        """Read APP_* values only, using a supplied mapping for deterministic tests."""
        env = os.environ if environ is None else environ
        environment = env.get("APP_ENV", "development").strip().lower()
        if environment not in {"development", "test", "production"}:
            raise ValueError("APP_ENV must be development, test, or production")

        log_level = env.get("APP_LOG_LEVEL", "INFO").strip().upper()
        if log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError("APP_LOG_LEVEL must be a valid Python log level")

        try:
            timeout = float(env.get("APP_REQUEST_TIMEOUT_SECONDS", "30"))
            retries = int(env.get("APP_MAX_RETRIES", "3"))
        except ValueError as exc:
            raise ValueError("Timeout must be numeric and retries must be an integer") from exc

        if not 0 < timeout <= 600:
            raise ValueError("APP_REQUEST_TIMEOUT_SECONDS must be in (0, 600]")
        if not 0 <= retries <= 10:
            raise ValueError("APP_MAX_RETRIES must be in [0, 10]")

        return cls(
            environment=environment,
            log_level=log_level,
            request_timeout_seconds=timeout,
            max_retries=retries,
        )
