from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

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
    patterns = sorted(path.parent for path in root.glob("[0-9][0-9]_*/**/pattern.yaml"))
    assert len(patterns) >= 105
    for pattern in patterns:
        assert (pattern / "README.md").is_file()
        assert (pattern / "pattern.yaml").is_file()
        entrypoint = pattern / "run.py"
        assert entrypoint.is_file()
        spec = importlib.util.spec_from_file_location(f"pattern_{len(patterns)}", entrypoint)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        if callable(getattr(module, "run", None)):
            result = module.run()  # type: ignore[no-untyped-call]
            assert result["offline"] is True  # type: ignore[index]
        else:
            assert callable(getattr(module, "main", None) or getattr(module, "demo", None))
