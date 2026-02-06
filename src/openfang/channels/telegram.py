"""Telegram channel implementation."""

from __future__ import annotations

import asyncio
import contextlib
import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any

from .models import ChannelInfo, ChannelStatus, InboundMessage

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from telegram.ext import Application

    MessageHandler = Callable[[InboundMessage], Awaitable[None]]

logger = logging.getLogger(__name__)


class TelegramChannel:
    """Telegram channel implementation using python-telegram-bot."""

    id = "telegram"

    def __init__(self) -> None:
        self._accounts: dict[str, dict[str, Any]] = {}
        # account_id -> {token, app, task, status}
        self._message_handler: MessageHandler | None = None

    def set_message_handler(self, handler: MessageHandler | None) -> None:
        """Set callback for inbound messages."""
        self._message_handler = handler

    def info(self) -> ChannelInfo:
        """Get channel info."""
        return ChannelInfo(
            id="telegram",
            name="Telegram",
            emoji="📱",
            description="Telegram Bot API",
            config_fields=["token"],
        )

    async def start(self, account_id: str) -> None:
        """Start a Telegram bot for an account."""
        if account_id not in self._accounts:
            raise ValueError(f"Account not configured: {account_id}")

        account = self._accounts[account_id]
        if account.get("running"):
            return

        token = account.get("token")
        if not token:
            raise ValueError(f"No token for account: {account_id}")

        from telegram.ext import Application, filters
        from telegram.ext import MessageHandler as TGMessageHandler

        app: Application = Application.builder().token(token).build()

        # Message handler that dispatches to callback
        async def handle_message(update, context):
            account["last_inbound_at"] = datetime.now()

            # Skip if no handler registered
            if not self._message_handler:
                return

            # Skip if no message text
            message = update.message or update.edited_message
            if not message or not message.text:
                return

            # Determine chat type
            chat = message.chat
            if chat.type == "private":
                chat_type = "direct"
            elif chat.type in ("group", "supergroup"):
                chat_type = "group"
            else:
                chat_type = "channel"

            # Create normalized inbound message
            inbound = InboundMessage(
                channel_id="telegram",
                account_id=account_id,
                sender_id=str(message.from_user.id) if message.from_user else "unknown",
                sender_name=message.from_user.full_name if message.from_user else None,
                target_id=str(chat.id),
                text=message.text,
                reply_to_id=str(message.reply_to_message.message_id) if message.reply_to_message else None,
                chat_type=chat_type,
                timestamp=message.date or datetime.now(),
            )

            # Dispatch to handler
            try:
                await self._message_handler(inbound)
            except Exception as e:
                logger.exception(f"Error in message handler: {e}")

        app.add_handler(TGMessageHandler(filters.TEXT, handle_message))

        # Start polling in background task
        async def run_polling():
            try:
                account["connected"] = True
                await app.initialize()
                await app.start()
                await app.updater.start_polling()
                # Keep running until stopped
                while account.get("running"):
                    await asyncio.sleep(1)
            except Exception as e:
                account["last_error"] = str(e)
                account["connected"] = False
                logger.exception(f"Telegram polling error for {account_id}")
            finally:
                account["connected"] = False
                try:
                    await app.updater.stop()
                    await app.stop()
                    await app.shutdown()
                except Exception:
                    pass

        account["running"] = True
        account["app"] = app
        account["task"] = asyncio.create_task(run_polling())
        account["last_error"] = None
        logger.info(f"Started Telegram account: {account_id}")

    async def stop(self, account_id: str) -> None:
        """Stop a Telegram bot."""
        if account_id not in self._accounts:
            return

        account = self._accounts[account_id]
        account["running"] = False

        task = account.get("task")
        if task and not task.done():
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

        account["connected"] = False
        account["app"] = None
        account["task"] = None
        logger.info(f"Stopped Telegram account: {account_id}")

    async def send(self, account_id: str, target: str, text: str) -> bool:
        """Send a message via Telegram."""
        if account_id not in self._accounts:
            return False

        account = self._accounts[account_id]
        app = account.get("app")
        if not app or not account.get("connected"):
            # Try direct send without app
            token = account.get("token")
            if token:
                try:
                    from telegram import Bot

                    bot = Bot(token=token)
                    await bot.send_message(chat_id=target, text=text)
                    account["last_outbound_at"] = datetime.now()
                    return True
                except Exception as e:
                    account["last_error"] = str(e)
                    return False
            return False

        try:
            await app.bot.send_message(chat_id=target, text=text)
            account["last_outbound_at"] = datetime.now()
            return True
        except Exception as e:
            account["last_error"] = str(e)
            return False

    async def status(self, account_id: str) -> ChannelStatus:
        """Get account status."""
        if account_id not in self._accounts:
            return ChannelStatus(
                account_id=account_id,
                channel_id="telegram",
                last_error="Account not configured",
            )

        account = self._accounts[account_id]
        return ChannelStatus(
            account_id=account_id,
            channel_id="telegram",
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
        """Configure a Telegram account."""
        self._accounts[account_id] = {
            "token": token,
            "name": name,
            "running": False,
            "connected": False,
            "app": None,
            "task": None,
            "last_inbound_at": None,
            "last_outbound_at": None,
            "last_error": None,
        }

    def remove_account(self, account_id: str) -> None:
        """Remove account configuration."""
        if account_id in self._accounts:
            del self._accounts[account_id]
