"""Discord channel implementation."""

from __future__ import annotations

import asyncio
import contextlib
import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any

from .models import ChannelInfo, ChannelStatus, InboundMessage

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    import discord

    MessageHandler = Callable[[InboundMessage], Awaitable[None]]

logger = logging.getLogger(__name__)


class DiscordChannel:
    """Discord channel implementation using discord.py."""

    id = "discord"

    def __init__(self) -> None:
        self._accounts: dict[str, dict[str, Any]] = {}
        # account_id -> {token, client, task, status, intents}
        self._message_handler: MessageHandler | None = None

    def set_message_handler(self, handler: MessageHandler | None) -> None:
        """Set callback for inbound messages."""
        self._message_handler = handler

    def info(self) -> ChannelInfo:
        """Get channel info."""
        return ChannelInfo(
            id="discord",
            name="Discord",
            emoji="🎮",
            description="Discord Bot API",
            config_fields=["token"],
        )

    async def start(self, account_id: str) -> None:
        """Start a Discord bot for an account."""
        if account_id not in self._accounts:
            raise ValueError(f"Account not configured: {account_id}")

        account = self._accounts[account_id]
        if account.get("running"):
            return

        token = account.get("token")
        if not token:
            raise ValueError(f"No token for account: {account_id}")

        import discord

        # Configure intents
        intents = discord.Intents.default()
        intents.message_content = True  # Required for reading message content

        client: discord.Client = discord.Client(intents=intents)

        @client.event
        async def on_ready():
            account["connected"] = True
            logger.info(f"Discord bot logged in as {client.user}")

        @client.event
        async def on_message(message: discord.Message):
            # Ignore bot's own messages
            if message.author == client.user:
                return

            account["last_inbound_at"] = datetime.now()

            # Skip if no handler registered
            if not self._message_handler:
                return

            # Skip if no text content
            if not message.content:
                return

            # Determine chat type
            if isinstance(message.channel, discord.DMChannel):
                chat_type = "direct"
                target_id = str(message.author.id)
            elif isinstance(message.channel, (discord.TextChannel, discord.Thread)):
                chat_type = "group"
                target_id = str(message.channel.id)
            else:
                chat_type = "channel"
                target_id = str(message.channel.id)

            # Create normalized inbound message
            inbound = InboundMessage(
                channel_id="discord",
                account_id=account_id,
                sender_id=str(message.author.id),
                sender_name=message.author.display_name,
                target_id=target_id,
                text=message.content,
                reply_to_id=str(message.reference.message_id) if message.reference else None,
                chat_type=chat_type,
                timestamp=message.created_at,
            )

            # Dispatch to handler
            try:
                await self._message_handler(inbound)
            except Exception as e:
                logger.exception(f"Error in message handler: {e}")

        @client.event
        async def on_disconnect():
            account["connected"] = False

        # Start client in background task
        async def run_client():
            try:
                account["connected"] = False
                await client.start(token)
            except Exception as e:
                account["last_error"] = str(e)
                account["connected"] = False
                logger.exception(f"Discord client error for {account_id}")
            finally:
                account["connected"] = False

        account["running"] = True
        account["client"] = client
        account["task"] = asyncio.create_task(run_client())
        account["last_error"] = None
        logger.info(f"Started Discord account: {account_id}")

    async def stop(self, account_id: str) -> None:
        """Stop a Discord bot."""
        if account_id not in self._accounts:
            return

        account = self._accounts[account_id]
        account["running"] = False

        client = account.get("client")
        if client and not client.is_closed():
            await client.close()

        task = account.get("task")
        if task and not task.done():
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

        account["connected"] = False
        account["client"] = None
        account["task"] = None
        logger.info(f"Stopped Discord account: {account_id}")

    async def send(self, account_id: str, target: str, text: str) -> bool:
        """Send a message via Discord.

        Args:
            account_id: The configured account ID.
            target: Channel ID or User ID to send to.
            text: Message text.
        """
        if account_id not in self._accounts:
            return False

        account = self._accounts[account_id]
        client = account.get("client")

        # Try to send with running client
        if client and account.get("connected"):
            try:
                target_id = int(target)
                channel = client.get_channel(target_id)
                if channel:
                    await channel.send(text)
                    account["last_outbound_at"] = datetime.now()
                    return True

                # Try as user DM
                user = client.get_user(target_id)
                if user:
                    dm = await user.create_dm()
                    await dm.send(text)
                    account["last_outbound_at"] = datetime.now()
                    return True

                # Fetch channel/user if not cached
                try:
                    channel = await client.fetch_channel(target_id)
                    await channel.send(text)
                    account["last_outbound_at"] = datetime.now()
                    return True
                except Exception:
                    pass

                try:
                    user = await client.fetch_user(target_id)
                    dm = await user.create_dm()
                    await dm.send(text)
                    account["last_outbound_at"] = datetime.now()
                    return True
                except Exception:
                    pass

                account["last_error"] = f"Could not find channel/user: {target}"
                return False

            except Exception as e:
                account["last_error"] = str(e)
                return False

        # No running client - try direct send
        token = account.get("token")
        if token:
            try:
                import discord

                intents = discord.Intents.default()
                client = discord.Client(intents=intents)

                async def send_and_close():
                    await client.login(token)
                    target_id = int(target)
                    channel = await client.fetch_channel(target_id)
                    await channel.send(text)
                    await client.close()

                await send_and_close()
                account["last_outbound_at"] = datetime.now()
                return True
            except Exception as e:
                account["last_error"] = str(e)
                return False

        return False

    async def status(self, account_id: str) -> ChannelStatus:
        """Get account status."""
        if account_id not in self._accounts:
            return ChannelStatus(
                account_id=account_id,
                channel_id="discord",
                last_error="Account not configured",
            )

        account = self._accounts[account_id]
        return ChannelStatus(
            account_id=account_id,
            channel_id="discord",
            name=account.get("name"),
            running=account.get("running", False),
            connected=account.get("connected", False),
            last_inbound_at=account.get("last_inbound_at"),
            last_outbound_at=account.get("last_outbound_at"),
            last_error=account.get("last_error"),
        )

    def configure_account(
        self,
        account_id: str,
        token: str,
        name: str | None = None,
    ) -> None:
        """Configure a Discord account.

        Args:
            account_id: Unique identifier for this account.
            token: Discord bot token.
            name: Optional display name.
        """
        self._accounts[account_id] = {
            "token": token,
            "name": name,
            "running": False,
            "connected": False,
            "client": None,
            "task": None,
            "last_inbound_at": None,
            "last_outbound_at": None,
            "last_error": None,
        }

    def remove_account(self, account_id: str) -> None:
        """Remove account configuration."""
        if account_id in self._accounts:
            del self._accounts[account_id]
