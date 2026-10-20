from __future__ import annotations

from pathlib import Path

import pytest

from applied_ai import AppliedAIClient, Message, MockProvider, Settings
from applied_ai.memory import ConversationMemory
from applied_ai.observability import EventRecorder
from applied_ai.providers import ProviderRegistry
from applied_ai.security import limit_text, redact_mapping


def test_client_uses_provider_neutral_contract() -> None:
    client = AppliedAIClient(MockProvider(default_text="ok"), "mock-model")
    assert client.ask("hello").text == "ok"


def test_settings_are_validated_and_secret_helpers_are_safe() -> None:
    settings = Settings.from_env({"AI_LAB_PROVIDER": "mock", "AI_LAB_MAX_RETRIES": "3"})
    assert settings.max_retries == 3
    assert redact_mapping({"API_KEY": "secret", "name": "demo"}) == {
        "API_KEY": "[REDACTED]",
        "name": "demo",
    }
    assert limit_text("abcdef", max_chars=3) == "abc"


def test_memory_registry_and_observability() -> None:
    memory = ConversationMemory(max_messages=1)
    memory.add(Message("user", "one"))
    memory.add(Message("user", "two"))
    assert tuple(message.content for message in memory.messages()) == ("two",)

    registry = ProviderRegistry()
    provider = MockProvider(default_text="registered")
    registry.register("demo", lambda: provider)
    assert registry.create("demo") is provider

    recorder = EventRecorder()
    assert recorder.record_call("mock", "mock-model", lambda: "ok") == "ok"
    assert recorder.snapshot()[0].success


def test_all_roadmap_pattern_manifests_have_runnable_entrypoints() -> None:
    root = Path(__file__).parents[1] / "engineering_patterns"
    patterns = [path for category in root.glob("0[1-8]_*") for path in category.iterdir() if path.is_dir()]
    assert len(patterns) >= 98
    for pattern in patterns:
        assert (pattern / "README.md").is_file()
        assert (pattern / "pattern.yaml").is_file()
        entrypoint = pattern / "run.py"
        assert entrypoint.is_file()
        namespace: dict[str, object] = {}
        exec(compile(entrypoint.read_text(encoding="utf-8"), str(entrypoint), "exec"), namespace)
        if "run" in namespace:
            result = namespace["run"]()  # type: ignore[operator]
            assert result["offline"] is True  # type: ignore[index]
        else:
            assert callable(namespace.get("main") or namespace.get("demo"))
