"""Tests for message routing."""

import pytest

from openfang.messaging.resolver import ResolvedRoute, RouteResolver


class TestRouteResolver:
    """Test route resolution logic."""

    @pytest.fixture
    def resolver(self):
        return RouteResolver()

    def test_resolve_direct_message(self, resolver):
        """Direct messages use sender_id as peer_id."""
        route = resolver.resolve(
            channel_id="telegram",
            account_id="bot-1",
            sender_id="user-123",
            target_id="user-123",
            peer_kind="direct",
        )

        assert route.session_key == "telegram:bot-1:direct:user-123"
        assert route.channel_id == "telegram"
        assert route.account_id == "bot-1"
        assert route.peer_id == "user-123"
        assert route.peer_kind == "direct"
        assert route.reply_target == "user-123"

    def test_resolve_group_message(self, resolver):
        """Group messages use target_id (group ID) as peer_id."""
        route = resolver.resolve(
            channel_id="telegram",
            account_id="bot-1",
            sender_id="user-123",
            target_id="group-456",
            peer_kind="group",
        )

        assert route.session_key == "telegram:bot-1:group:group-456"
        assert route.peer_id == "group-456"
        assert route.reply_target == "group-456"

    def test_resolve_channel_message(self, resolver):
        """Channel messages use target_id as peer_id."""
        route = resolver.resolve(
            channel_id="discord",
            account_id="bot-2",
            sender_id="user-789",
            target_id="channel-101",
            peer_kind="channel",
        )

        assert route.session_key == "discord:bot-2:channel:channel-101"
        assert route.peer_id == "channel-101"

    def test_resolve_different_channels_different_sessions(self, resolver):
        """Same user on different channels gets different sessions."""
        telegram_route = resolver.resolve(
            channel_id="telegram",
            account_id="bot-1",
            sender_id="user-123",
            target_id="user-123",
        )

        discord_route = resolver.resolve(
            channel_id="discord",
            account_id="bot-1",
            sender_id="user-123",
            target_id="user-123",
        )

        assert telegram_route.session_key != discord_route.session_key

    def test_resolve_different_accounts_different_sessions(self, resolver):
        """Same user on different accounts gets different sessions."""
        route1 = resolver.resolve(
            channel_id="telegram",
            account_id="bot-1",
            sender_id="user-123",
            target_id="user-123",
        )

        route2 = resolver.resolve(
            channel_id="telegram",
            account_id="bot-2",
            sender_id="user-123",
            target_id="user-123",
        )

        assert route1.session_key != route2.session_key

    def test_resolve_default_peer_kind_is_direct(self, resolver):
        """Default peer_kind is 'direct'."""
        route = resolver.resolve(
            channel_id="telegram",
            account_id="bot-1",
            sender_id="user-123",
            target_id="user-123",
        )

        assert route.peer_kind == "direct"


class TestResolvedRoute:
    """Test ResolvedRoute dataclass."""

    def test_resolved_route_fields(self):
        route = ResolvedRoute(
            session_key="telegram:bot:direct:user",
            channel_id="telegram",
            account_id="bot",
            peer_id="user",
            peer_kind="direct",
            reply_target="user",
        )

        assert route.session_key == "telegram:bot:direct:user"
        assert route.channel_id == "telegram"
        assert route.account_id == "bot"
        assert route.peer_id == "user"
        assert route.peer_kind == "direct"
        assert route.reply_target == "user"
