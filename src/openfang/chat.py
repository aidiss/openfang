"""Chat helper for multi-turn conversations."""

from __future__ import annotations

from typing import TYPE_CHECKING

import logfire
from pydantic_ai import UsageLimits

from .capabilities import InMemoryConversations

if TYPE_CHECKING:
    from .deps import Deps

# Default limits for safety
DEFAULT_USAGE_LIMITS = UsageLimits(
    request_limit=25,
    response_tokens_limit=8000,
)


async def chat(
    deps: Deps,
    user_message: str,
    usage_limits: UsageLimits | None = None,
) -> str:
    """
    Run a chat turn, managing conversation history automatically.

    - Loads message history from deps.conversations if conversation_id is set
    - Runs agent with history
    - Saves new messages back to conversations
    - Returns the agent's response
    """
    from .agent import default_agent as agent

    limits = usage_limits or DEFAULT_USAGE_LIMITS
    conv_id = deps.conversation_id

    with logfire.span(
        "chat",
        conversation_id=conv_id,
        user_id=deps.user.id,
        message_preview=user_message[:100],
    ):
        # Load existing history if we have a conversation
        message_history = []
        if conv_id:
            message_history = await deps.storage.conversations.get(conv_id)
            logfire.info("loaded history", message_count=len(message_history))

        # Run agent with history
        result = await agent.run(
            user_message,
            deps=deps,
            message_history=message_history or None,
            usage_limits=limits,
        )

        # Save new messages if we have a conversation
        if conv_id:
            await deps.storage.conversations.append(conv_id, result.new_messages())

        logfire.info(
            "chat complete",
            response_preview=result.output[:100],
            new_messages=len(result.new_messages()),
        )

        return result.output


async def start_conversation(deps: Deps, conversation_id: str) -> None:
    """Start or resume a conversation."""
    deps.conversation_id = conversation_id
    if isinstance(deps.storage.conversations, InMemoryConversations):
        deps.storage.conversations.associate_user(conversation_id, deps.user.id)
