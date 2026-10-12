"""Deterministic mock backend and fault sequence."""

from __future__ import annotations

import pytest

from applied_ai import LLMRequest, Message, MockProvider, TokenUsage
from applied_ai.core.exceptions import CapabilityNotSupportedError, RateLimitError
from applied_ai.core.requests import StructuredOutputSpec


def test_mock_returns_keyed_response_and_metadata() -> None:
    provider = MockProvider(
        responses={"ping": "pong"},
        usage=TokenUsage(input_tokens=2, output_tokens=3, total_tokens=5),
    )
    request = LLMRequest("local-test", (Message("user", "ping"),))
    first = provider.generate(request)
    second = provider.generate(request)
    assert (first.text, first.request_id, second.request_id) == ("pong", "mock-0001", "mock-0002")
    assert first.usage == TokenUsage(2, 3, 5)
    assert first.latency_seconds == 0.0
    assert provider.call_count == 2


def test_faults_injected_in_call_order_no_automatic_retry() -> None:
    provider = MockProvider(faults=[RateLimitError("synthetic", provider="mock")])
    request = LLMRequest("demo", (Message("user", "ping"),))
    with pytest.raises(RateLimitError) as error:
        provider.generate(request)
    assert error.value.retryable is True
    assert provider.call_count == 1
    assert provider.generate(request).text == "Mock response"
    assert provider.call_count == 2


def test_unsupported_structured_output_fails_before_call() -> None:
    provider = MockProvider(supports_structured_output=False)
    spec = StructuredOutputSpec("result", {"type": "object"})
    request = LLMRequest("mock", (Message("user", "hi"),), response_format=spec)
    with pytest.raises(CapabilityNotSupportedError):
        provider.generate(request)
    assert provider.call_count == 0
