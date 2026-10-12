"""OpenAI adapter tests use MockTransport: no outgoing network requests."""

from __future__ import annotations

import json

import httpx
import pytest

from applied_ai import LLMRequest, Message, StructuredOutputSpec
from applied_ai.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConfigurationError,
    InvalidRequestError,
    InvalidStructuredOutputError,
    ModelRefusalError,
    ProviderConnectionError,
    ProviderResponseError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    RateLimitError,
)
from applied_ai.providers.openai_provider import OpenAIProvider


def example_response(text: str = "Hello!") -> dict[str, object]:
    return {
        "id": "resp_example",
        "model": "test-model",
        "status": "completed",
        "output": [
            {"type": "reasoning", "summary": []},
            {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": text}],
            },
        ],
        "usage": {"input_tokens": 12, "output_tokens": 5, "total_tokens": 17},
    }


def make_provider(handler: httpx.MockTransport) -> OpenAIProvider:
    return OpenAIProvider(
        api_key="test-placeholder-not-a-real-secret",
        client=httpx.Client(transport=handler),
    )


def test_http_request_and_usage_normalization() -> None:
    calls: list[dict[str, object]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert str(request.url) == "https://api.openai.com/v1/responses"
        assert request.headers["authorization"].startswith("Bearer ")
        data: dict[str, object] = json.loads(request.content)
        calls.append(data)
        return httpx.Response(200, json=example_response())

    provider = make_provider(httpx.MockTransport(handler))
    result = provider.generate(
        LLMRequest(
            "test-model",
            (Message("system", "Be brief"), Message("user", "Hi")),
            max_output_tokens=70,
        )
    )
    assert result.text == "Hello!"
    assert result.model == "test-model"
    assert result.provider == "openai"
    assert result.finish_reason == "completed"
    assert result.request_id == "resp_example"
    assert result.usage is not None
    assert (
        result.usage.input_tokens,
        result.usage.output_tokens,
        result.usage.total_tokens,
    ) == (12, 5, 17)
    assert result.latency_seconds is not None and result.latency_seconds >= 0
    assert calls == [
        {
            "model": "test-model",
            "input": [{"role": "system", "content": "Be brief"}, {"role": "user", "content": "Hi"}],
            "store": False,
            "max_output_tokens": 70,
        }
    ]


def test_structured_format_is_sent_and_result_verified() -> None:
    spec = StructuredOutputSpec(
        "answer",
        {
            "type": "object",
            "properties": {"value": {"type": "integer"}},
            "required": ["value"],
            "additionalProperties": False,
        },
    )

    def handler(request: httpx.Request) -> httpx.Response:
        data = json.loads(request.content)
        assert data["text"]["format"] == {
            "type": "json_schema",
            "name": "answer",
            "schema": dict(spec.schema),
            "strict": True,
        }
        return httpx.Response(200, json=example_response('{"value": 9}'))

    result = make_provider(httpx.MockTransport(handler)).generate(
        LLMRequest("test-model", (Message("user", "solve"),), response_format=spec)
    )
    assert result.parsed_output == {"value": 9}


def test_schema_mismatch_is_not_silent() -> None:
    spec = StructuredOutputSpec("answer", {"type": "object", "required": ["ok"]})
    provider = make_provider(
        httpx.MockTransport(lambda _: httpx.Response(200, json=example_response("{}")))
    )
    with pytest.raises(InvalidStructuredOutputError):
        provider.generate(LLMRequest("test", (Message("user", "hi"),), response_format=spec))


@pytest.mark.parametrize(
    ("status", "expected", "retryable"),
    [
        (400, InvalidRequestError, False),
        (401, AuthenticationError, False),
        (403, AuthorizationError, False),
        (404, InvalidRequestError, False),
        (408, ProviderTimeoutError, True),
        (409, ProviderUnavailableError, True),
        (429, RateLimitError, True),
        (500, ProviderUnavailableError, True),
        (503, ProviderUnavailableError, True),
    ],
)
def test_http_error_mapping(status: int, expected: type[Exception], retryable: bool) -> None:
    calls = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(
            status, headers={"x-request-id": "req_test"}, json={"error": "do not log"}
        )

    provider = make_provider(httpx.MockTransport(handler))
    with pytest.raises(expected) as error:
        provider.generate(LLMRequest("test", (Message("user", "hello"),)))
    assert error.value.retryable is retryable  # type: ignore[attr-defined]
    assert error.value.request_id == "req_test"  # type: ignore[attr-defined]
    assert "do not log" not in str(error.value)
    assert calls == 1


def test_timeout_maps_to_category() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("read timeout")

    with pytest.raises(ProviderTimeoutError):
        make_provider(httpx.MockTransport(handler)).generate(
            LLMRequest("test", (Message("user", "hello"),))
        )


def test_connection_error_maps_to_category() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("offline")

    with pytest.raises(ProviderConnectionError):
        make_provider(httpx.MockTransport(handler)).generate(
            LLMRequest("test", (Message("user", "hello"),))
        )


@pytest.mark.parametrize(
    "payload",
    ["not json", "[]", '{"status":"failed"}', '{"status":"completed","output": []}'],
)
def test_malformed_or_incomplete_response(payload: str) -> None:
    provider = make_provider(httpx.MockTransport(lambda _: httpx.Response(200, text=payload)))
    with pytest.raises(ProviderResponseError):
        provider.generate(LLMRequest("test", (Message("user", "hello"),)))


def test_refusal_is_distinct_from_transport_error() -> None:
    body = example_response()
    body["output"] = [{"type": "message", "content": [{"type": "refusal", "refusal": "No"}]}]
    provider = make_provider(httpx.MockTransport(lambda _: httpx.Response(200, json=body)))
    with pytest.raises(ModelRefusalError):
        provider.generate(LLMRequest("test", (Message("user", "hello"),)))


def test_missing_key_is_explicit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ConfigurationError):
        OpenAIProvider()
