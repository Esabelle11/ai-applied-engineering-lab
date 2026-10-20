"""Validated execution of an allowlisted model-requested function."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    description: str
    parameters: Mapping[str, Any]

    def __post_init__(self) -> None:
        if not self.name.isidentifier() or not self.description.strip():
            raise ValueError("Tool name must be an identifier and description must be non-empty")
        if self.parameters.get("type") != "object":
            raise ValueError("Tool parameters must be an object JSON Schema")
        Draft202012Validator.check_schema(dict(self.parameters))


@dataclass(frozen=True, slots=True)
class ToolCall:
    name: str
    arguments: Mapping[str, Any]


def execute_tool_call(
    call: ToolCall, tools: Mapping[str, tuple[ToolSpec, Callable[..., object]]]
) -> object:
    """Validate arguments, then invoke only a caller-supplied allowlisted tool."""
    if call.name not in tools:
        raise PermissionError(f"Tool is not allowlisted: {call.name}")
    specification, function = tools[call.name]
    try:
        Draft202012Validator(dict(specification.parameters)).validate(dict(call.arguments))
    except ValidationError as exc:
        raise ValueError(f"Invalid arguments for {call.name}") from exc
    return function(**dict(call.arguments))


def main() -> None:
    weather = ToolSpec(
        "weather_for_city",
        "Return a synthetic temperature for a city.",
        {"type": "object", "properties": {"city": {"type": "string", "minLength": 1}}, "required": ["city"], "additionalProperties": False},
    )
    result = execute_tool_call(ToolCall("weather_for_city", {"city": "Kuala Lumpur"}), {"weather_for_city": (weather, lambda city: f"{city}: 31°C")})
    print(result)


if __name__ == "__main__":
    main()
