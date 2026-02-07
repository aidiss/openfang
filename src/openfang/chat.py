"""Chat helper for multi-turn sessions."""

from __future__ import annotations

from typing import TYPE_CHECKING

import logfire
from pydantic_ai import UsageLimits

from .capabilities import InMemorySessions

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
    Run a chat turn, managing session history automatically.

    - Loads message history from deps.sessions if session_id is set
    - Runs agent with history
    - Saves new messages back to sessions
    - Returns the agent's response
    """
    from .agent import default_agent as agent

    limits = usage_limits or DEFAULT_USAGE_LIMITS
    session_id = deps.session_id

    with logfire.span(
        "chat",
        session_id=session_id,
        user_id=deps.user.id,
        message_preview=user_message[:100],
    ):
        # Load existing history if we have a session
        message_history = []
        if session_id:
            message_history = await deps.storage.sessions.get(session_id)
            logfire.info("loaded history", message_count=len(message_history))

        # Run agent with history
        result = await agent.run(
            user_message,
            deps=deps,
            message_history=message_history or None,
            usage_limits=limits,
        )

        # Save new messages if we have a session
        if session_id:
            await deps.storage.sessions.append(session_id, result.new_messages())

        logfire.info(
            "chat complete",
            response_preview=result.output[:100],
            new_messages=len(result.new_messages()),
        )

        return result.output


async def start_session(deps: Deps, session_id: str) -> None:
    """Start or resume a session."""
    deps.session_id = session_id
    if isinstance(deps.storage.sessions, InMemorySessions):
        deps.storage.sessions.associate_user(session_id, deps.user.id)
