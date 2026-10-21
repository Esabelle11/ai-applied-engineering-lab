"""Normalize a small provider payload into the Lab's shared response contract."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from applied_ai import LLMResponse, TokenUsage


def _optional_text(value: object, field: str) -> str | None:
    if value is not None and not isinstance(value, str):
        raise ValueError(f"{field} must be text or None")
    return value


def normalize_response(payload: Mapping[str, Any], *, provider: str, model: str) -> LLMResponse:
    """Convert a provider payload only when all observed values have safe, expected types."""
    text = payload.get("text")
    if not isinstance(text, str):
        raise ValueError("payload.text must be text")
    usage_data = payload.get("usage")
    if usage_data is not None and not isinstance(usage_data, Mapping):
        raise ValueError("payload.usage must be a mapping")
    usage = None
    if usage_data is not None:
        usage = TokenUsage(
            input_tokens=usage_data.get("input_tokens"),
            output_tokens=usage_data.get("output_tokens"),
            total_tokens=usage_data.get("total_tokens"),
        )
    latency = payload.get("latency_seconds")
    if latency is not None and (not isinstance(latency, (int, float)) or latency < 0):
        raise ValueError("latency_seconds must be a non-negative number")
    return LLMResponse(
        text=text,
        provider=provider,
        model=model,
        request_id=_optional_text(payload.get("request_id"), "request_id"),
        finish_reason=_optional_text(payload.get("finish_reason"), "finish_reason"),
        usage=usage,
        latency_seconds=float(latency) if latency is not None else None,
    )


def main() -> None:
    response = normalize_response(
        {
            "text": "Normalized answer",
            "usage": {"input_tokens": 4, "output_tokens": 2, "total_tokens": 6},
        },
        provider="example",
        model="example-model",
    )
    print("response:", response)
    print(f"{response.provider}/{response.model}: {response.text}")


if __name__ == "__main__":
    main()
