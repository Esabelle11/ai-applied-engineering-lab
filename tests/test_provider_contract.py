"""The same request/response contract works with independent adapters."""

from __future__ import annotations

import httpx
import pytest

from applied_ai import LLMRequest, Message, MockProvider
from applied_ai.core.protocols import LLMProvider
from applied_ai.providers.openai_provider import OpenAIProvider


@pytest.mark.parametrize("backend", ["mock", "openai"])
def test_common_sync_generation_contract(backend: str) -> None:
    prompt = "Hi"
    request = LLMRequest(model="contract-test", messages=(Message("user", prompt),))
    if backend == "mock":
        provider: LLMProvider = MockProvider(default_text="Hello")
    else:
        body = {
            "id": "resp_contract",
            "model": "contract-test",
            "status": "completed",
            "output": [{"type": "message", "content": [{"type": "output_text", "text": "Hello"}]}],
        }
        provider = OpenAIProvider(
            api_key="dummy-contract-fixture",
            client=httpx.Client(
                transport=httpx.MockTransport(lambda _: httpx.Response(200, json=body))
            ),
        )
    assert isinstance(provider, LLMProvider)
    response = provider.generate(request)
    assert response.text == "Hello"
    assert response.model == request.model
    assert response.provider == provider.name
    assert response.request_id is not None
