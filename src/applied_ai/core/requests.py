"""Validated, immutable generation requests and structured-output specifications."""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

from applied_ai.core.messages import Message


@dataclass(frozen=True, slots=True)
class StructuredOutputSpec:
    """Object JSON Schema for API-enforced and locally validated JSON output."""

    name: str
    schema: Mapping[str, Any]
    strict: bool = True

    def __post_init__(self) -> None:
        if (
            not self.name
            or len(self.name) > 64
            or not all(char.isascii() and (char.isalnum() or char in "_-") for char in self.name)
        ):
            raise ValueError("Schema name must be 1–64 ASCII letters, numbers, _ or -")
        if not isinstance(self.schema, Mapping) or self.schema.get("type") != "object":
            raise ValueError("Structured output requires an object JSON Schema")
        try:
            Draft202012Validator.check_schema(dict(self.schema))
        except SchemaError as exc:
            raise ValueError("Invalid JSON Schema") from exc


@dataclass(frozen=True, slots=True)
class LLMRequest:
    model: str
    messages: tuple[Message, ...]
    max_output_tokens: int | None = None
    temperature: float | None = None
    response_format: StructuredOutputSpec | None = None
    timeout_seconds: float | None = None
    reasoning_effort: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.model, str) or not self.model.strip():
            raise ValueError("Model must be a non-empty string")
        if not isinstance(self.messages, tuple) or not self.messages:
            raise ValueError("Messages must be a non-empty tuple")
        if not all(isinstance(message, Message) for message in self.messages):
            raise TypeError("Every message must be a Message")
        if self.max_output_tokens is not None and (
            type(self.max_output_tokens) is not int or self.max_output_tokens < 1
        ):
            raise ValueError("max_output_tokens must be a positive integer")
        if self.temperature is not None and not 0 <= self.temperature <= 2:
            raise ValueError("temperature must be within [0, 2]")
        if self.timeout_seconds is not None and (
            not math.isfinite(self.timeout_seconds) or self.timeout_seconds <= 0
        ):
            raise ValueError("timeout_seconds must be finite and positive")
