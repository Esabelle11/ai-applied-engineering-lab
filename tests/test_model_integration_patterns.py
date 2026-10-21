"""Offline behavior checks for the expanded model-integration patterns."""

from __future__ import annotations

import asyncio
import importlib.util
import sys
from pathlib import Path

import pytest

from applied_ai import LLMRequest, Message, MockProvider
from applied_ai.core.exceptions import ConfigurationError

ROOT = Path(__file__).parents[1] / "engineering_patterns" / "02_model_integration"


def load_pattern(name: str):  # type: ignore[no-untyped-def]
    path = ROOT / name / "run.py"
    module_name = f"model_pattern_{name}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_function_calling_validates_tool_name_and_json_arguments() -> None:
    pattern = load_pattern("function_calling")
    spec = pattern.ToolSpec(
        "add",
        "Add two integers",
        {
            "type": "object",
            "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
            "required": ["a", "b"],
            "additionalProperties": False,
        },
    )
    assert (
        pattern.execute_tool_call(
            pattern.ToolCall("add", {"a": 2, "b": 3}), {"add": (spec, lambda a, b: a + b)}
        )
        == 5
    )
    with pytest.raises(PermissionError):
        pattern.execute_tool_call(pattern.ToolCall("delete", {}), {})
    with pytest.raises(ValueError):
        pattern.execute_tool_call(
            pattern.ToolCall("add", {"a": "two", "b": 3}), {"add": (spec, lambda a, b: a + b)}
        )


def test_local_inference_is_offline_by_default() -> None:
    pattern = load_pattern("local_model_inference")
    assert (
        pattern.infer(pattern.create_local_provider(), "mock", "hello")
        == "Local-model demonstration response"
    )
    with pytest.raises(ConfigurationError):
        pattern.create_local_provider(live=True, base_url="file:///tmp/model")


def test_response_normalization_preserves_normalized_fields() -> None:
    pattern = load_pattern("model_response_normalization")
    response = pattern.normalize_response(
        {
            "text": "ok",
            "usage": {"input_tokens": 1, "output_tokens": 2, "total_tokens": 3},
            "latency_seconds": 0.2,
        },
        provider="test",
        model="test-model",
    )
    assert (response.text, response.usage.total_tokens, response.latency_seconds) == ("ok", 3, 0.2)
    with pytest.raises(ValueError):
        pattern.normalize_response({"text": 7}, provider="test", model="model")


def test_multimodal_payload_requires_safe_image_scheme() -> None:
    pattern = load_pattern("multimodal_input")
    content = pattern.to_openai_content(
        (pattern.TextPart("describe"), pattern.ImagePart("https://example.test/image.png"))
    )
    assert content[1]["type"] == "input_image"
    with pytest.raises(ValueError):
        pattern.ImagePart("file:///tmp/image.png")


def test_parallel_execution_preserves_call_order() -> None:
    pattern = load_pattern("parallel_model_execution")
    calls = (
        pattern.ModelCall(
            MockProvider(default_text="first"), LLMRequest("first", (Message("user", "A"),))
        ),
        pattern.ModelCall(
            MockProvider(default_text="second"), LLMRequest("second", (Message("user", "B"),))
        ),
    )
    assert [
        result.text for result in asyncio.run(pattern.execute_parallel(calls, max_concurrency=2))
    ] == ["first", "second"]
    with pytest.raises(ValueError):
        asyncio.run(pattern.execute_parallel((), max_concurrency=1))


def test_provider_abstraction_uses_common_contract() -> None:
    pattern = load_pattern("provider_abstraction")
    registry = pattern.create_registry()
    assert (
        pattern.generate_reply(registry.create("detailed"), "mock", "Explain RAG").text
        == "Detailed answer"
    )


def test_streaming_enforces_order_and_terminal_signal() -> None:
    pattern = load_pattern("streaming_responses")
    provider = pattern.MockStreamingProvider("hello", chunk_size=2)
    assert pattern.collect_stream(provider.stream("greet")) == "hello"
    with pytest.raises(ValueError):
        pattern.collect_stream(iter((pattern.StreamChunk(0, "partial"),)))
