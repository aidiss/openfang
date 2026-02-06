"""Centralized settings using pydantic-settings."""

import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """OpenFang gateway settings.

    All settings can be overridden via environment variables with OPENFANG_ prefix,
    or via a .env file in the working directory.
    """

    model_config = SettingsConfigDict(
        env_prefix="OPENFANG_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Gateway server
    host: str = "127.0.0.1"
    port: int = 18789

    # LLM Model configuration
    model: str = "openai:gpt-4o"
    """Model string (e.g. 'openai:gpt-4o', 'anthropic:claude-sonnet-4-20250514').
    If PYDANTIC_AI_GATEWAY_API_KEY is set, automatically prefixes with 'gateway/'."""

    # Heartbeat
    heartbeat_enabled: bool = True
    heartbeat_interval: int = 1800  # 30 minutes
    heartbeat_prompt: str = "Check HEARTBEAT.md if it exists. If nothing needs attention, reply exactly: HEARTBEAT_OK"
    heartbeat_ack_token: str = "HEARTBEAT_OK"
    heartbeat_ack_max_len: int = 300

    # Logfire
    logfire_enabled: bool = True
    logfire_service_name: str = "openfang-gateway"

    # Channel tokens (optional - auto-configure channels if set)
    telegram_bot_token: str | None = None
    discord_bot_token: str | None = None

    # Webhooks
    webhooks_enabled: bool = False
    webhooks_token: str | None = None
    """Token required for webhook authentication. Set to enable webhooks."""

    # CLI user identity (optional)
    user_email: str = "cli@local"
    user_phone: str | None = None
    user_telegram: str | None = None

    def get_model(self) -> str:
        """Get the effective model string, with gateway prefix if configured."""
        model = self.model

        # If gateway key is set and model doesn't already have gateway prefix, add it
        if os.environ.get("PYDANTIC_AI_GATEWAY_API_KEY") and not model.startswith("gateway/"):
            return f"gateway/{model}"

        return model


# Singleton instance
settings = Settings()
