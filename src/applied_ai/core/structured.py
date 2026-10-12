"""Provider-independent JSON decoding and schema validation."""

from __future__ import annotations

import json
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from applied_ai.core.exceptions import InvalidStructuredOutputError
from applied_ai.core.requests import StructuredOutputSpec


def parse_structured_output(
    text: str, specification: StructuredOutputSpec, *, provider: str
) -> dict[str, Any]:
    try:
        parsed: Any = json.loads(text)
    except json.JSONDecodeError as exc:
        raise InvalidStructuredOutputError(
            "Provider did not return valid JSON", provider=provider
        ) from exc
    if not isinstance(parsed, dict):
        raise InvalidStructuredOutputError(
            "Structured response must be a JSON object", provider=provider
        )
    try:
        Draft202012Validator(dict(specification.schema)).validate(parsed)
    except ValidationError as exc:
        raise InvalidStructuredOutputError(
            "Structured response does not match requested schema", provider=provider
        ) from exc
    return parsed
