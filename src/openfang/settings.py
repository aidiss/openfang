"""Centralized settings using pydantic-settings."""

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

    # Gateway
    host: str = "127.0.0.1"
    port: int = 18789

    # Heartbeat
    heartbeat_enabled: bool = True
    heartbeat_interval: int = 1800  # 30 minutes in seconds

    # Logfire
    logfire_enabled: bool = True
    logfire_service_name: str = "openfang-gateway"

    # Channel tokens (optional - auto-configure channels if set)
    telegram_bot_token: str | None = None
    discord_bot_token: str | None = None


# Singleton instance
settings = Settings()
