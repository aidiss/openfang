"""Google Chat channel stub - not yet implemented."""

from __future__ import annotations

from .models import ChannelInfo, ChannelStatus


class GoogleChatChannel:
    """Google Chat channel stub (not implemented).

    Full implementation would use Google Chat API with
    service account authentication for Workspace apps.
    """

    id = "googlechat"
    implemented = False

    def __init__(self) -> None:
        self._accounts: dict[str, dict] = {}
        self._message_handler = None

    def set_message_handler(self, handler) -> None:
        """Set callback for inbound messages (no-op for stub)."""
        self._message_handler = handler

    def info(self) -> ChannelInfo:
        """Get channel info."""
        return ChannelInfo(
            id="googlechat",
            name="Google Chat",
            emoji="💬",
            description="Google Workspace Chat API (coming soon)",
            config_fields=["service_account_key", "project_id"],
        )

    async def start(self, account_id: str) -> None:
        """Start Google Chat - not implemented."""
        raise NotImplementedError(
            "Google Chat channel is not yet implemented. " "Requires Google Chat API with service account credentials."
        )

    async def stop(self, account_id: str) -> None:
        """Stop Google Chat - not implemented."""
        raise NotImplementedError("Google Chat channel is not yet implemented.")

    async def send(self, account_id: str, target: str, text: str) -> bool:
        """Send via Google Chat - not implemented."""
        raise NotImplementedError("Google Chat channel is not yet implemented.")

    async def status(self, account_id: str) -> ChannelStatus:
        """Get account status."""
        return ChannelStatus(
            account_id=account_id,
            channel_id="googlechat",
            last_error="Channel not implemented",
        )
