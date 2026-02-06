"""Signal channel stub - not yet implemented."""

from __future__ import annotations

from .models import ChannelInfo, ChannelStatus


class SignalChannel:
    """Signal channel stub (not implemented).

    Full implementation would use signal-cli REST API
    with a linked device for message sending/receiving.
    """

    id = "signal"
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
            id="signal",
            name="Signal",
            emoji="📶",
            description="Signal via signal-cli REST API (coming soon)",
            config_fields=["signal_cli_url", "phone_number"],
        )

    async def start(self, account_id: str) -> None:
        """Start Signal - not implemented."""
        raise NotImplementedError(
            "Signal channel is not yet implemented. " "Requires signal-cli REST API running as a linked device."
        )

    async def stop(self, account_id: str) -> None:
        """Stop Signal - not implemented."""
        raise NotImplementedError("Signal channel is not yet implemented.")

    async def send(self, account_id: str, target: str, text: str) -> bool:
        """Send via Signal - not implemented."""
        raise NotImplementedError("Signal channel is not yet implemented.")

    async def status(self, account_id: str) -> ChannelStatus:
        """Get account status."""
        return ChannelStatus(
            account_id=account_id,
            channel_id="signal",
            last_error="Channel not implemented",
        )
