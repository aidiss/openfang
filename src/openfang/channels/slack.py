"""Slack channel stub - not yet implemented."""

from __future__ import annotations

from .models import ChannelInfo, ChannelStatus


class SlackChannel:
    """Slack channel stub (not implemented).

    Full implementation would use Slack Bolt SDK with Socket Mode
    for real-time messaging without a public endpoint.
    """

    id = "slack"
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
            id="slack",
            name="Slack",
            emoji="#️⃣",
            description="Slack Bot via Socket Mode (coming soon)",
            config_fields=["bot_token", "app_token"],
        )

    async def start(self, account_id: str) -> None:
        """Start Slack - not implemented."""
        raise NotImplementedError("Slack channel is not yet implemented. " "Requires Slack Bolt SDK with Socket Mode.")

    async def stop(self, account_id: str) -> None:
        """Stop Slack - not implemented."""
        raise NotImplementedError("Slack channel is not yet implemented.")

    async def send(self, account_id: str, target: str, text: str) -> bool:
        """Send via Slack - not implemented."""
        raise NotImplementedError("Slack channel is not yet implemented.")

    async def status(self, account_id: str) -> ChannelStatus:
        """Get account status."""
        return ChannelStatus(
            account_id=account_id,
            channel_id="slack",
            last_error="Channel not implemented",
        )
