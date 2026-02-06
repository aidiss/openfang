"""Tests for settings."""

from openfang.settings import Settings


def test_settings_defaults():
    s = Settings()
    assert s.host == "127.0.0.1"
    assert s.port == 18789
    assert s.heartbeat_enabled is True
    assert s.heartbeat_interval == 1800
    assert s.logfire_enabled is True
    assert s.logfire_service_name == "openfang-gateway"
    assert s.telegram_bot_token is None
    assert s.discord_bot_token is None


def test_settings_env_prefix(monkeypatch):
    monkeypatch.setenv("OPENFANG_HOST", "0.0.0.0")
    monkeypatch.setenv("OPENFANG_PORT", "8080")
    monkeypatch.setenv("OPENFANG_HEARTBEAT_ENABLED", "false")

    s = Settings()
    assert s.host == "0.0.0.0"
    assert s.port == 8080
    assert s.heartbeat_enabled is False
