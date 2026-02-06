"""Route resolution - map inbound messages to agent sessions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass
class ResolvedRoute:
    """Resolved routing information for an inbound message."""

    session_key: str
    """Unique session key for conversation persistence."""

    channel_id: str
    """Channel the message came from (telegram, discord, etc.)."""

    account_id: str
    """Account that received the message."""

    peer_id: str
    """Sender's unique ID on the channel."""

    peer_kind: Literal["direct", "group", "channel"]
    """Type of conversation."""

    reply_target: str
    """Where to send the response (chat_id, channel_id, etc.)."""


class RouteResolver:
    """Resolves inbound messages to agent sessions.

    Session key format: `{channel}:{account}:{peer_kind}:{peer_id}`

    This creates isolated conversations per:
    - Channel (telegram vs discord)
    - Account (different bot tokens)
    - Conversation type (DM vs group)
    - Peer (user or group ID)
    """

    def resolve(
        self,
        channel_id: str,
        account_id: str,
        sender_id: str,
        target_id: str,
        peer_kind: Literal["direct", "group", "channel"] = "direct",
    ) -> ResolvedRoute:
        """Resolve routing for an inbound message.

        Args:
            channel_id: Channel identifier (telegram, discord, etc.)
            account_id: Account that received the message
            sender_id: Sender's unique ID
            target_id: Chat/group/channel ID where message was sent
            peer_kind: Type of conversation

        Returns:
            ResolvedRoute with session key and reply target
        """
        # For direct messages, the peer is the sender
        # For groups/channels, the peer is the group/channel
        if peer_kind == "direct":
            peer_id = sender_id
        else:
            peer_id = target_id

        session_key = f"{channel_id}:{account_id}:{peer_kind}:{peer_id}"

        return ResolvedRoute(
            session_key=session_key,
            channel_id=channel_id,
            account_id=account_id,
            peer_id=peer_id,
            peer_kind=peer_kind,
            reply_target=target_id,
        )
