"""OpenAI HTTP mock integration for the reliability wrapper (never network)."""

from __future__ import annotations

import httpx
import pytest

from applied_ai import LLMRequest, Message
from applied_ai.core.exceptions import AuthenticationError, RequestDeadlineExceededError
from applied_ai.providers.openai_provider import OpenAIProvider, _parse_retry_after
from applied_ai.reliability import ReliableProvider, RetryPolicy


def request() -> LLMRequest:
    return LLMRequest("test-model", (Message("user", "Hi"),))


def result_payload() -> dict[str, object]:
    return {
        "id": "r-test",
        "model": "test-model",
        "status": "completed",
        "output": [{"type": "message", "content": [{"type": "output_text", "text": "ok"}]}],
        "usage": {"input_tokens": 2, "output_tokens": 1, "total_tokens": 3},
    }


def test_429_retry_after_followed_by_success() -> None:
    calls = 0
    delays: list[float] = []

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(429, headers={"retry-after": "2", "x-request-id": "r429"})
        return httpx.Response(200, json=result_payload())

    provider = OpenAIProvider(
        api_key="fake-test-key", client=httpx.Client(transport=httpx.MockTransport(handler))
    )
    wrapped = ReliableProvider(
        provider,
        policy=RetryPolicy(max_attempts=2),
        sleep=delays.append,
        total_timeout_seconds=10,
    )
    response = wrapped.generate(request())
    assert response.text == "ok"
    assert calls == 2 and delays == [2]
    assert response.reliability is not None and response.reliability.attempts == 2
    assert response.usage is not None and response.usage.total_tokens == 3


def test_invalid_auth_does_not_retry() -> None:
    calls = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(401)

    provider = OpenAIProvider(
        api_key="fake-test-key", client=httpx.Client(transport=httpx.MockTransport(handler))
    )
    with pytest.raises(AuthenticationError):
        ReliableProvider(provider, policy=RetryPolicy(max_attempts=4)).generate(request())
    assert calls == 1


def test_http_timeout_capped_by_request_budget() -> None:
    timeouts: list[float] = []

    def handler(req: httpx.Request) -> httpx.Response:
        timeouts.append(req.extensions["timeout"]["read"])
        return httpx.Response(200, json=result_payload())

    provider = OpenAIProvider(
        api_key="fake-test-key",
        timeout_seconds=30,
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    ReliableProvider(provider, total_timeout_seconds=3).generate(request())
    assert len(timeouts) == 1 and 0 < timeouts[0] <= 3


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("0", 0.0), ("3", 3.0), ("-2", 0.0), ("invalid", None), ("NaN", None)],
)
def test_retry_after_parser(raw: str, expected: float | None) -> None:
    assert _parse_retry_after(raw) == expected


def test_empty_deadline_budget_prevents_http_call() -> None:
    # Very short deadline + Retry-After must never create a second request.
    calls = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(503, headers={"retry-after": "60"})

    provider = OpenAIProvider(
        api_key="fake-test-key", client=httpx.Client(transport=httpx.MockTransport(handler))
    )
    with pytest.raises(RequestDeadlineExceededError):
        ReliableProvider(provider, total_timeout_seconds=0.5).generate(request())
    assert calls == 1
