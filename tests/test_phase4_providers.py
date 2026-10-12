"""Phase 4 HTTP adapters and no-credential provider switching."""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from applied_ai.core import LLMRequest, Message, StructuredOutputSpec
from applied_ai.core.exceptions import (
    AuthenticationError,
    CapabilityNotSupportedError,
    ConfigurationError,
    ProviderResponseError,
    RateLimitError,
)
from applied_ai.providers.anthropic_provider import AnthropicProvider
from applied_ai.providers.factory import ProviderFactory, read_dotenv
from applied_ai.providers.google_provider import GoogleProvider
from applied_ai.providers.ollama_provider import OllamaProvider
from applied_ai.providers.openrouter_provider import OpenRouterProvider

REQ = LLMRequest(
    "example-model", (Message("system", "Be clear"), Message("user", "Hello")), max_output_tokens=32
)


def make_client(handler: object) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler))  # type: ignore[arg-type]


def test_openrouter_normalizes_and_uses_correct_endpoint() -> None:
    requests: list[dict[str, object]] = []

    def respond(req: httpx.Request) -> httpx.Response:
        assert req.url == "https://openrouter.ai/api/v1/chat/completions"
        assert req.headers["Authorization"] == "Bearer fake"
        requests.append(json.loads(req.content))
        return httpx.Response(
            200,
            json={
                "id": "id1",
                "model": "example-model",
                "choices": [{"message": {"content": "Hello!"}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 5, "completion_tokens": 2, "total_tokens": 7},
            },
        )

    with make_client(respond) as http:
        provider = OpenRouterProvider(api_key="fake", client=http)
        result = provider.generate(REQ)
        assert result.text == "Hello!" and result.usage is not None
        assert result.usage.total_tokens == 7
        assert requests[0]["model"] == "example-model"
        assert requests[0]["messages"] == [
            {"role": "system", "content": "Be clear"},
            {"role": "user", "content": "Hello"},
        ]


def test_openrouter_rejects_unsupported_json_schema_before_http() -> None:
    def fail(_: httpx.Request) -> httpx.Response:
        raise AssertionError("No HTTP call expected")

    with make_client(fail) as http:
        provider = OpenRouterProvider(api_key="fake", client=http)
        schema = StructuredOutputSpec("answer", {"type": "object"})
        req = LLMRequest("m", (Message("user", "x"),), response_format=schema)
        with pytest.raises(CapabilityNotSupportedError):
            provider.generate(req)


@pytest.mark.parametrize("status,error", [(401, AuthenticationError), (429, RateLimitError)])
def test_openrouter_normalized_errors(status: int, error: type[Exception]) -> None:
    def respond(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status,
            headers={"Retry-After": "2", "x-request-id": "rid"},
            json={"secret": "must-not-echo"},
        )

    with make_client(respond) as http:
        with pytest.raises(error) as exc:
            OpenRouterProvider(api_key="fake", client=http).generate(REQ)
        assert "must-not-echo" not in str(exc.value)
        if status == 429:
            assert exc.value.retry_after_seconds == 2


def test_anthropic_messages_and_usage() -> None:
    def respond(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/v1/messages"
        assert req.headers["anthropic-version"] == "2023-06-01"
        body = json.loads(req.content)
        assert body["system"] == "Be clear"
        assert body["messages"] == [{"role": "user", "content": "Hello"}]
        return httpx.Response(
            200,
            json={
                "id": "msg1",
                "model": "example-model",
                "content": [{"type": "text", "text": "Hi!"}],
                "stop_reason": "end_turn",
                "usage": {"input_tokens": 3, "output_tokens": 2},
            },
        )

    with make_client(respond) as http:
        result = AnthropicProvider(api_key="fake", client=http).generate(REQ)
        assert result.text == "Hi!" and result.usage is not None
        assert result.usage.input_tokens == 3


def test_google_payload_and_usage() -> None:
    def respond(req: httpx.Request) -> httpx.Response:
        assert req.url.path.endswith("/models/example-model:generateContent")
        assert req.headers["x-goog-api-key"] == "fake"
        body = json.loads(req.content)
        assert body["systemInstruction"]["parts"][0]["text"] == "Be clear"
        return httpx.Response(
            200,
            json={
                "candidates": [
                    {"content": {"parts": [{"text": "Gemini here"}]}, "finishReason": "STOP"}
                ],
                "usageMetadata": {
                    "promptTokenCount": 5,
                    "candidatesTokenCount": 2,
                    "totalTokenCount": 7,
                },
            },
        )

    with make_client(respond) as http:
        result = GoogleProvider(api_key="fake", client=http).generate(REQ)
        assert result.text == "Gemini here" and result.usage is not None
        assert result.usage.total_tokens == 7


def test_ollama_local_endpoint_and_rejection_of_remote() -> None:
    with pytest.raises(ValueError):
        OllamaProvider(base_url="http://example.com:11434")

    def respond(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/api/chat"
        assert json.loads(req.content)["stream"] is False
        return httpx.Response(
            200, json={"message": {"content": "Local"}, "model": "llama3.2", "eval_count": 4}
        )

    with make_client(respond) as http:
        result = OllamaProvider(client=http).generate(REQ)
        assert result.provider == "ollama" and result.text == "Local"


def test_bad_provider_response_is_categorized() -> None:
    with (
        make_client(lambda _: httpx.Response(200, json={"choices": []})) as http,
        pytest.raises(ProviderResponseError),
    ):
        OpenRouterProvider(api_key="fake", client=http).generate(REQ)


def test_factory_defaults_to_no_network_and_guards_live(tmp_path: Path) -> None:
    config = ProviderFactory(env={}, dotenv=tmp_path / "absent")
    result = config.create()
    assert result.provider.generate(REQ).text == "Mock response"
    assert config.model == "mock-model"
    live = ProviderFactory(
        env={"AI_LAB_PROVIDER": "openrouter", "OPENROUTER_API_KEY": "fake"},
        dotenv=tmp_path / "absent",
    )
    assert live.model == "nvidia/nemotron-3.5-lightning:free"
    with pytest.raises(ConfigurationError, match="--live"):
        live.create()
    with pytest.raises(ConfigurationError):
        ProviderFactory(env={"AI_LAB_PROVIDER": "not-valid"}, dotenv=tmp_path / "absent")


def test_dotenv_environment_precedence(tmp_path: Path) -> None:
    dot = tmp_path / ".env"
    dot.write_text(
        "# local only\nAI_LAB_PROVIDER='openrouter'\nAI_LAB_MODEL=sample:free\n", encoding="utf-8"
    )
    assert read_dotenv(dot)["AI_LAB_MODEL"] == "sample:free"
    factory = ProviderFactory(env={"AI_LAB_PROVIDER": "mock"}, dotenv=dot)
    assert factory.kind == "mock" and factory.model == "sample:free"


def test_credentials_missing_is_safe(tmp_path: Path) -> None:
    for kind in ("openrouter", "anthropic", "google", "openai"):
        factory = ProviderFactory(env={"AI_LAB_PROVIDER": kind}, dotenv=tmp_path / "absent")
        with pytest.raises(ConfigurationError):
            factory.create(allow_live=True)
