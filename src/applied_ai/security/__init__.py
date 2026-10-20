"""Input and secret-safety helpers shared by examples and applications."""

from __future__ import annotations

import re

_SECRET_KEY = re.compile(r"(api[_-]?key|token|secret|password)", re.IGNORECASE)


def redact_mapping(values: dict[str, str]) -> dict[str, str]:
    """Return a copy with secret-looking keys redacted."""
    return {key: ("[REDACTED]" if _SECRET_KEY.search(key) else value) for key, value in values.items()}


def limit_text(value: str, *, max_chars: int = 10_000) -> str:
    if max_chars < 1:
        raise ValueError("max_chars must be positive")
    return value[:max_chars]
