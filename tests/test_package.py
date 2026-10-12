"""Verify importable package and explicit public exports."""

import applied_ai


def test_package_has_explicit_exports() -> None:
    assert applied_ai.__version__ == "0.8.0"
    assert "ProviderFactory" in applied_ai.__all__
    assert "RuntimeConfig" in applied_ai.__all__
    assert "MockProvider" in applied_ai.__all__
    assert "LLMRequest" in applied_ai.__all__
    assert applied_ai.RuntimeConfig is not None
