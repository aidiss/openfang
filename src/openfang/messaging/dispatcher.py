"""Message dispatcher - route inbound messages to agent and send responses."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Awaitable, Callable

from .resolver import ResolvedRoute, RouteResolver

if TYPE_CHECKING:
    from ..channels.models import InboundMessage
    from ..deps import Deps
    from ..models import User
    from ..protocols import Channels

logger = logging.getLogger(__name__)

# Type alias for message handler callback
MessageHandler = Callable[["InboundMessage"], Awaitable[None]]


class UnauthorizedUserError(Exception):
    """Raised when user is not authorized to use the bot."""

    pass


def _create_user_from_message(message: "InboundMessage") -> "User":
    """Create a User from an inbound message with proper authorization.

    Args:
        message: The inbound message containing sender info

    Returns:
        User with appropriate roles based on settings

    Raises:
        UnauthorizedUserError: If user is not the owner
    """
    from ..models import Role, User
    from ..settings import settings

    # Check if user is the owner
    if message.channel_id == "telegram":
        sender_id = message.sender_id

        if not settings.user_telegram:
            raise UnauthorizedUserError("No owner configured. Set OPENFANG_USER_TELEGRAM.")

        if sender_id != settings.user_telegram:
            raise UnauthorizedUserError(f"User {sender_id} ({message.sender_name}) is not authorized.")

        # Owner gets admin role
        roles = {Role.ADMIN, Role.DEVELOPER}
    else:
        # For other channels, reject by default (can be extended later)
        raise UnauthorizedUserError(f"Channel {message.channel_id} authorization not configured.")

    # Create user with real info from message
    return User(
        id=int(message.sender_id) if message.sender_id.isdigit() else 0,
        email=f"{message.sender_id}@{message.channel_id}",
        roles=roles,
        telegram_id=message.sender_id if message.channel_id == "telegram" else None,
    )


def _create_deps_for_message(message: "InboundMessage", session_key: str) -> "Deps":
    """Create deps for a specific message/request.

    This is called per-message to create isolated deps for the agent run.

    Args:
        message: The inbound message to create deps for
        session_key: The session key for session tracking

    Returns:
        Deps container with authorized user

    Raises:
        UnauthorizedUserError: If user is not authorized
    """
    from ..deps import CommsAdapters, Deps, SchedulingAdapters, StorageAdapters, WebAdapters, WorkspaceAdapters

    user = _create_user_from_message(message)
    root = Path.cwd()

    return Deps(
        user=user,
        session_id=session_key,
        storage=StorageAdapters.default(root),
        web_adapters=WebAdapters.default(),
        workspace=WorkspaceAdapters.default(root),
        scheduling=SchedulingAdapters.default(),
        comms=CommsAdapters.default(),
    )


class MessageDispatcher:
    """Dispatches inbound messages to agent and sends responses back.

    This is the central message router that:
    1. Receives inbound messages from channels
    2. Resolves routing (session key, reply target)
    3. Creates deps for the request
    4. Runs the agent with message context
    5. Sends the response back to the channel

    Note: Does NOT hold deps - creates them per-request.
    """

    def __init__(
        self,
        channels: Channels,
        resolver: RouteResolver | None = None,
    ) -> None:
        self.channels = channels
        self.resolver = resolver or RouteResolver()

    async def handle_message(self, message: InboundMessage) -> None:
        """Handle an inbound message from any channel.

        Args:
            message: Normalized inbound message from channel
        """
        logger.info(
            "Received message",
            extra={
                "channel": message.channel_id,
                "account": message.account_id,
                "sender": message.sender_id,
                "target": message.target_id,
                "text_preview": message.text[:50] if message.text else "",
            },
        )

        # Resolve routing
        route = self.resolver.resolve(
            channel_id=message.channel_id,
            account_id=message.account_id,
            sender_id=message.sender_id,
            target_id=message.target_id,
            peer_kind=message.chat_type,
        )

        try:
            # Run agent and get response
            response = await self._dispatch_to_agent(message, route)

            # Send response back to channel
            if response:
                await self._send_response(route, response)

        except UnauthorizedUserError as e:
            logger.warning(
                "Unauthorized user",
                extra={
                    "session_key": route.session_key,
                    "sender_id": message.sender_id,
                    "sender_name": message.sender_name,
                    "error": str(e),
                },
            )
            await self._send_response(route, f"Access denied: {e}")

        except Exception as e:
            logger.exception(
                "Error handling message",
                extra={"session_key": route.session_key, "error": str(e)},
            )
            # Optionally send error message back
            await self._send_response(route, f"Sorry, I encountered an error: {type(e).__name__}")

    async def _dispatch_to_agent(self, message: InboundMessage, route: ResolvedRoute) -> str | None:
        """Dispatch message to agent and return response.

        Args:
            message: The inbound message
            route: Resolved routing information

        Returns:
            Agent response text, or None if no response
        """
        from ..chat import chat, start_session

        # Create deps for this request (validates user authorization)
        deps = _create_deps_for_message(message, route.session_key)

        # Set up session context
        await start_session(deps, route.session_key)

        # Run agent
        response = await chat(deps, message.text)

        return response

    async def _send_response(self, route: ResolvedRoute, text: str) -> None:
        """Send response back to the channel.

        Args:
            route: Routing information with reply target
            text: Response text to send
        """
        channel = self.channels.get_channel(route.channel_id)
        if not channel:
            logger.error(f"Channel not found: {route.channel_id}")
            return

        try:
            success = await channel.send(
                account_id=route.account_id,
                target=route.reply_target,
                text=text,
            )
            if not success:
                logger.warning(f"Failed to send response to {route.channel_id}:{route.reply_target}")
        except Exception as e:
            logger.exception(f"Error sending response: {e}")

    def create_handler(self) -> MessageHandler:
        """Create a message handler callback for channels.

        Returns:
            Async callback function that handles InboundMessage
        """
        return self.handle_message
