"""Validate no-secret configuration without modifying the host environment."""

import pytest

from applied_ai import RuntimeConfig


def test_default_config_is_deterministic() -> None:
    config = RuntimeConfig.from_env({})
    assert config.environment == "development"
    assert config.request_timeout_seconds == 30
    assert config.max_retries == 3


def test_non_secret_values_are_parsed() -> None:
    config = RuntimeConfig.from_env(
        {
            "APP_ENV": "TEST",
            "APP_LOG_LEVEL": "warning",
            "APP_REQUEST_TIMEOUT_SECONDS": "5.5",
            "APP_MAX_RETRIES": "2",
            "OPENAI_API_KEY": "not-read-or-logged",
        }
    )
    assert config.environment == "test"
    assert config.log_level == "WARNING"
    assert config.request_timeout_seconds == 5.5
    assert config.max_retries == 2
    assert "not-read-or-logged" not in repr(config)


@pytest.mark.parametrize(
    ("settings", "message"),
    [
        ({"APP_ENV": "invalid"}, "APP_ENV"),
        ({"APP_LOG_LEVEL": "VERBOSE"}, "APP_LOG_LEVEL"),
        ({"APP_REQUEST_TIMEOUT_SECONDS": "0"}, "APP_REQUEST_TIMEOUT_SECONDS"),
        ({"APP_REQUEST_TIMEOUT_SECONDS": "NaN"}, "APP_REQUEST_TIMEOUT_SECONDS"),
        ({"APP_MAX_RETRIES": "11"}, "APP_MAX_RETRIES"),
        ({"APP_MAX_RETRIES": "two"}, "Timeout must be numeric"),
    ],
)
def test_bad_config_rejected(settings: dict[str, str], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        RuntimeConfig.from_env(settings)
