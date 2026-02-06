"""WhatsApp channel stub - not yet implemented."""

from __future__ import annotations

from .models import ChannelInfo, ChannelStatus


class WhatsAppChannel:
    """WhatsApp channel stub (not implemented).

    Full implementation would use WhatsApp Web via QR code pairing,
    similar to OpenClaw's Baileys-based implementation.
    """

    id = "whatsapp"
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
            id="whatsapp",
            name="WhatsApp",
            emoji="📱",
            description="WhatsApp Web via QR code (coming soon)",
            config_fields=["phone_number"],
        )

    async def start(self, account_id: str) -> None:
        """Start WhatsApp - not implemented."""
        raise NotImplementedError(
            "WhatsApp channel is not yet implemented. "
            "Requires WhatsApp Web integration via Baileys or similar library."
        )

    async def stop(self, account_id: str) -> None:
        """Stop WhatsApp - not implemented."""
        raise NotImplementedError("WhatsApp channel is not yet implemented.")

    async def send(self, account_id: str, target: str, text: str) -> bool:
        """Send via WhatsApp - not implemented."""
        raise NotImplementedError("WhatsApp channel is not yet implemented.")

    async def status(self, account_id: str) -> ChannelStatus:
        """Get account status."""
        return ChannelStatus(
            account_id=account_id,
            channel_id="whatsapp",
            last_error="Channel not implemented",
        )
