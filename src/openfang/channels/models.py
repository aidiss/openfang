"""Channel data models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class ChannelAccount(BaseModel):
    """A configured account on a channel."""

    id: str
    channel_id: str  # "telegram", "discord", "slack"
    name: str | None = None
    enabled: bool = True
    config: dict[str, Any] = Field(default_factory=dict)
    """Channel-specific config (token, webhook_url, etc.)."""


class ChannelStatus(BaseModel):
    """Runtime status of a channel account."""

    account_id: str
    channel_id: str
    name: str | None = None
    running: bool = False
    connected: bool = False
    last_inbound_at: datetime | None = None
    last_outbound_at: datetime | None = None
    last_error: str | None = None


class InboundMessage(BaseModel):
    """Normalized inbound message from any channel."""

    channel_id: str
    account_id: str
    sender_id: str
    sender_name: str | None = None
    target_id: str
    """Chat/group/channel ID where the message was sent."""

    text: str
    reply_to_id: str | None = None
    chat_type: Literal["direct", "group", "channel"] = "direct"
    timestamp: datetime = Field(default_factory=datetime.now)


class ChannelInfo(BaseModel):
    """Static info about a channel type."""

    id: str
    name: str
    emoji: str = ""
    description: str = ""
    config_fields: list[str] = Field(default_factory=list)
    """Fields needed for account config (e.g., ['token'] for Telegram)."""
