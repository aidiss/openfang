"""Message dispatcher - route inbound messages to agent and send responses."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Awaitable, Callable

from .resolver import ResolvedRoute, RouteResolver

if TYPE_CHECKING:
    from ..channels.models import InboundMessage
    from ..protocols import Channels

logger = logging.getLogger(__name__)

# Type alias for message handler callback
MessageHandler = Callable[["InboundMessage"], Awaitable[None]]


def _create_deps_for_session(session_key: str):
    """Create deps for a specific session/request.

    This is called per-message to create isolated deps for the agent run.
    """
    from ..deps import CommsAdapters, Deps, SchedulingAdapters, StorageAdapters, WebAdapters, WorkspaceAdapters
    from ..models import User

    user = User(id=0, email="channel@system", roles={"admin"})
    root = Path.cwd()

    return Deps(
        user=user,
        conversation_id=session_key,
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
        from ..chat import chat, start_conversation

        # Create deps for this request
        deps = _create_deps_for_session(route.session_key)

        # Set up conversation context
        await start_conversation(deps, route.session_key)

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
