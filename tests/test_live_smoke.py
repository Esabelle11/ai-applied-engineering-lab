"""Explicitly opt-in billable live-provider smoke test. Skipped in normal CI."""

from __future__ import annotations

import os

import pytest

from applied_ai import LLMRequest, Message


def test_openai_live_smoke() -> None:
    if os.getenv("AI_LAB_RUN_LIVE_TESTS") != "1":
        pytest.skip("Set AI_LAB_RUN_LIVE_TESTS=1 to opt into live API smoke testing")
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY is not configured")
    from applied_ai.providers.openai_provider import OpenAIProvider

    model = os.environ.get("AI_LAB_LIVE_MODEL", "gpt-4.1-mini")
    with OpenAIProvider(timeout_seconds=20) as provider:
        response = provider.generate(
            LLMRequest(model, (Message("user", "Reply with exactly: pong"),), max_output_tokens=20)
        )
    assert response.text.strip()
    assert response.provider == "openai"
