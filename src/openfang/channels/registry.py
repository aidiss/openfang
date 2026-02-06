"""Channel registry - manages channel implementations and accounts."""

from __future__ import annotations

import contextlib
import logging
from typing import TYPE_CHECKING

from .models import ChannelAccount, ChannelInfo, ChannelStatus, InboundMessage

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from ..protocols import Channel

    MessageHandler = Callable[[InboundMessage], Awaitable[None]]

logger = logging.getLogger(__name__)


class ChannelRegistry:
    """Manages channel implementations and their accounts."""

    def __init__(self) -> None:
        self._channels: dict[str, Channel] = {}
        self._accounts: dict[str, ChannelAccount] = {}  # key: f"{channel_id}:{account_id}"

    @classmethod
    def default(cls) -> ChannelRegistry:
        """Create registry with all channels, auto-configured from settings."""
        from ..settings import settings
        from .discord import DiscordChannel
        from .googlechat import GoogleChatChannel
        from .imessage import IMessageChannel
        from .signal import SignalChannel
        from .slack import SlackChannel
        from .telegram import TelegramChannel
        from .whatsapp import WhatsAppChannel

        registry = cls()

        # Implemented channels (auto-configure if token set)
        telegram = TelegramChannel()
        if settings.telegram_bot_token:
            telegram.configure_account("default", settings.telegram_bot_token)
        registry.register_channel(telegram)

        discord = DiscordChannel()
        if settings.discord_bot_token:
            discord.configure_account("default", settings.discord_bot_token)
        registry.register_channel(discord)

        # Stub channels
        for channel_cls in [WhatsAppChannel, SlackChannel, GoogleChatChannel, SignalChannel, IMessageChannel]:
            registry.register_channel(channel_cls())

        return registry

    def register_channel(self, channel: Channel) -> None:
        """Register a channel implementation."""
        self._channels[channel.id] = channel
        logger.debug(f"Registered channel: {channel.id}")

    def get_channel(self, channel_id: str) -> Channel | None:
        """Get a channel by ID."""
        return self._channels.get(channel_id)

    def list_channels(self) -> list[ChannelInfo]:
        """List all registered channels."""
        return [ch.info() for ch in self._channels.values()]

    async def add_account(self, account: ChannelAccount) -> None:
        """Add an account to a channel."""
        channel = self._channels.get(account.channel_id)
        if not channel:
            raise ValueError(f"Unknown channel: {account.channel_id}")

        key = f"{account.channel_id}:{account.id}"
        self._accounts[key] = account
        logger.info(f"Added account: {key}")

    async def remove_account(self, channel_id: str, account_id: str) -> None:
        """Remove an account."""
        key = f"{channel_id}:{account_id}"
        if key in self._accounts:
            # Stop if running
            channel = self._channels.get(channel_id)
            if channel:
                with contextlib.suppress(Exception):
                    await channel.stop(account_id)
            del self._accounts[key]
            logger.info(f"Removed account: {key}")

    async def list_accounts(self, channel_id: str | None = None) -> list[ChannelAccount]:
        """List accounts, optionally filtered by channel."""
        if channel_id:
            return [acc for acc in self._accounts.values() if acc.channel_id == channel_id]
        return list(self._accounts.values())

    async def start_account(self, channel_id: str, account_id: str) -> None:
        """Start a channel account."""
        channel = self._channels.get(channel_id)
        if not channel:
            raise ValueError(f"Unknown channel: {channel_id}")

        key = f"{channel_id}:{account_id}"
        if key not in self._accounts:
            raise ValueError(f"Unknown account: {key}")

        await channel.start(account_id)
        logger.info(f"Started account: {key}")

    async def stop_account(self, channel_id: str, account_id: str) -> None:
        """Stop a channel account."""
        channel = self._channels.get(channel_id)
        if not channel:
            raise ValueError(f"Unknown channel: {channel_id}")

        key = f"{channel_id}:{account_id}"
        await channel.stop(account_id)
        logger.info(f"Stopped account: {key}")

    async def status(self) -> list[ChannelStatus]:
        """Get status of all accounts."""
        statuses = []
        for account in self._accounts.values():
            channel = self._channels.get(account.channel_id)
            if channel:
                try:
                    st = await channel.status(account.id)
                    statuses.append(st)
                except Exception as e:
                    statuses.append(
                        ChannelStatus(
                            account_id=account.id,
                            channel_id=account.channel_id,
                            name=account.name,
                            last_error=str(e),
                        )
                    )
        return statuses

    def get_account(self, channel_id: str, account_id: str) -> ChannelAccount | None:
        """Get a specific account."""
        key = f"{channel_id}:{account_id}"
        return self._accounts.get(key)

    def set_message_handler(self, handler: MessageHandler | None) -> None:
        """Set message handler callback on all registered channels.

        Args:
            handler: Async callback called with InboundMessage, or None to clear.
        """
        for channel in self._channels.values():
            if hasattr(channel, "set_message_handler"):
                channel.set_message_handler(handler)
        logger.debug(f"Set message handler on {len(self._channels)} channels")
