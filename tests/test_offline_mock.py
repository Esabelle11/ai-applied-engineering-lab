"""Smoke-test offline fixtures."""

from typing import Any


def test_mock_fixture_has_predictable_output(mock_llm_response: dict[str, Any]) -> None:
    assert mock_llm_response["model"] == "fake-model-v1"
    assert mock_llm_response["output_text"] == "A deterministic mock response for offline tests."
    assert mock_llm_response["usage"]["input_tokens"] == 10
