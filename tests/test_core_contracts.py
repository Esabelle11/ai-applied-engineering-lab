"""Offline request model, schema, and provider protocol tests."""

from __future__ import annotations

import pytest

from applied_ai import LLMRequest, Message, MockProvider, StructuredOutputSpec
from applied_ai.core import LLMProvider, TokenUsage
from applied_ai.core.exceptions import InvalidStructuredOutputError


@pytest.fixture
def schema_spec() -> StructuredOutputSpec:
    return StructuredOutputSpec(
        name="answer",
        schema={
            "type": "object",
            "properties": {"answer": {"type": "integer"}},
            "required": ["answer"],
            "additionalProperties": False,
        },
    )


def test_request_is_immutable_and_provider_protocol() -> None:
    request = LLMRequest("demo", (Message("user", "Hi"),))
    provider = MockProvider()
    assert isinstance(provider, LLMProvider)
    assert provider.generate(request).text == "Mock response"
    with pytest.raises(AttributeError):
        request.model = "other"  # type: ignore[misc]


@pytest.mark.parametrize("role", ["bad", "tool", ""])
def test_unsupported_roles_fail(role: str) -> None:
    with pytest.raises(ValueError):
        Message(role, "Hello")  # type: ignore[arg-type]


@pytest.mark.parametrize("messages", [(), ("hello",)])
def test_invalid_messages_fail(messages: tuple[object, ...]) -> None:
    with pytest.raises((ValueError, TypeError)):
        LLMRequest("demo", messages)  # type: ignore[arg-type]


@pytest.mark.parametrize("kwargs", [{"model": ""}, {"max_output_tokens": 0}, {"temperature": 3}])
def test_invalid_request_settings_fail(kwargs: dict[str, object]) -> None:
    config: dict[str, object] = {"model": "demo", "messages": (Message("user", "Hi"),)}
    config.update(kwargs)
    with pytest.raises(ValueError):
        LLMRequest(**config)  # type: ignore[arg-type]


def test_invalid_schema_rejected_on_construction() -> None:
    with pytest.raises(ValueError):
        StructuredOutputSpec("bad name!", {"type": "object"})
    with pytest.raises(ValueError):
        StructuredOutputSpec("test", {"type": "array"})
    with pytest.raises(ValueError):
        StructuredOutputSpec("test", {"type": "object", "properties": {"x": {"type": "??"}}})


def test_usage_counts_are_not_estimated() -> None:
    response = MockProvider().generate(LLMRequest("demo", (Message("user", "Hi"),)))
    assert response.usage is None
    with pytest.raises(ValueError):
        TokenUsage(input_tokens=-1)


def test_structured_output_is_validated_not_just_parsed(schema_spec: StructuredOutputSpec) -> None:
    request = LLMRequest("demo", (Message("user", "Calculate"),), response_format=schema_spec)
    good = MockProvider(default_text='{"answer": 42}').generate(request)
    assert good.parsed_output == {"answer": 42}
    for bad_text in ('{"answer": "42"}', '{"answer": 42, "extra": 0}', "[42]", "{broken"):
        with pytest.raises(InvalidStructuredOutputError):
            MockProvider(default_text=bad_text).generate(request)
