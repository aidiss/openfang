"""Telegram bot runner."""

from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from telegram import Update
    from telegram import User as TelegramUser

    from ..deps import Deps
    from ..protocols import Conversations, Cron


@dataclass
class UpdateInfo:
    """Normalized info extracted from a Telegram update."""

    chat_id: int
    user: TelegramUser
    text: str | None = None
    message_id: int | None = None


def get_update_info(update: Update) -> UpdateInfo | None:
    """Extract normalized info from any Telegram update type."""
    sources = [
        update.message,
        update.edited_message,
        update.callback_query,
        update.channel_post,
    ]
    for src in sources:
        if not src:
            continue
        # callback_query has message nested
        msg = getattr(src, "message", src)
        user = getattr(src, "from_user", None)
        if msg and user and hasattr(msg, "chat_id"):
            return UpdateInfo(
                chat_id=msg.chat_id,
                user=user,
                text=getattr(msg, "text", None) or getattr(src, "data", None),
                message_id=getattr(msg, "message_id", None),
            )
    return None


@asynccontextmanager
async def deps_from_telegram(
    update: Update,
    *,
    conversations: Conversations,
    cron: Cron,
    token: str,
) -> AsyncIterator[tuple[Deps, UpdateInfo] | tuple[None, None]]:
    """Create Deps from a Telegram update."""
    from ..chat import start_conversation
    from ..deps import create_deps
    from ..models import User

    info = get_update_info(update)
    if not info:
        yield None, None
        return

    user = User(
        id=info.user.id,
        email=f"{info.user.username or info.user.id}@telegram",
        roles={"user"},
    )
    conv_id = f"telegram-{info.chat_id}"

    async with create_deps(
        user=user,
        conversations=conversations,
        cron=cron,
        telegram_token=token,
        conversation_id=conv_id,
    ) as deps:
        await start_conversation(deps, conv_id)
        yield deps, info


async def run_telegram_bot(
    token: str,
    conversations: Conversations | None = None,
    cron: Cron | None = None,
):
    """
    Run Telegram bot that listens for messages and responds via agent.

    Each Telegram chat gets its own conversation thread.
    """
    from telegram.ext import Application, CommandHandler, MessageHandler, filters

    from ..capabilities import InMemoryConversations, InMemoryCron
    from ..chat import chat

    conversations = conversations or InMemoryConversations()
    cron = cron or InMemoryCron()

    async def handle_message(update: Update, context) -> None:
        async with deps_from_telegram(
            update,
            conversations=conversations,
            cron=cron,
            token=token,
        ) as (deps, info):
            if not deps or not info or not info.text:
                return
            response = await chat(deps, info.text)

        await update.message.reply_text(response)

    async def handle_start(update: Update, context) -> None:
        await update.message.reply_text("Hello! I'm your AI assistant. Send me a message and I'll help you.")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Telegram bot starting...")
    await app.run_polling()
