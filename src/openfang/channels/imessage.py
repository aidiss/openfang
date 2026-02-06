"""iMessage channel stub - not yet implemented."""

from __future__ import annotations

from .models import ChannelInfo, ChannelStatus


class IMessageChannel:
    """iMessage channel stub (not implemented).

    Full implementation would use AppleScript on macOS
    or BlueBubbles server for cross-platform support.
    """

    id = "imessage"
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
            id="imessage",
            name="iMessage",
            emoji="🍎",
            description="iMessage via AppleScript/BlueBubbles (coming soon)",
            config_fields=["applescript_enabled"],
        )

    async def start(self, account_id: str) -> None:
        """Start iMessage - not implemented."""
        raise NotImplementedError(
            "iMessage channel is not yet implemented. " "Requires macOS with AppleScript or BlueBubbles server."
        )

    async def stop(self, account_id: str) -> None:
        """Stop iMessage - not implemented."""
        raise NotImplementedError("iMessage channel is not yet implemented.")

    async def send(self, account_id: str, target: str, text: str) -> bool:
        """Send via iMessage - not implemented."""
        raise NotImplementedError("iMessage channel is not yet implemented.")

    async def status(self, account_id: str) -> ChannelStatus:
        """Get account status."""
        return ChannelStatus(
            account_id=account_id,
            channel_id="imessage",
            last_error="Channel not implemented",
        )
