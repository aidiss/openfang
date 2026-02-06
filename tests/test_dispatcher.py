"""Tests for message dispatcher."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from openfang.channels.models import InboundMessage
from openfang.messaging.dispatcher import MessageDispatcher


class TestMessageDispatcher:
    """Test message dispatcher."""

    @pytest.fixture
    def mock_channels(self):
        """Create mock channels registry."""
        channels = MagicMock()
        mock_channel = MagicMock()
        mock_channel.send = AsyncMock(return_value=True)
        channels.get_channel.return_value = mock_channel
        return channels

    @pytest.fixture
    def dispatcher(self, mock_channels):
        return MessageDispatcher(channels=mock_channels)

    @pytest.fixture
    def sample_message(self):
        return InboundMessage(
            channel_id="telegram",
            account_id="bot-1",
            sender_id="user-123",
            sender_name="Test User",
            target_id="user-123",
            text="Hello, bot!",
            chat_type="direct",
            timestamp=datetime.now(),
        )

    def test_create_handler_returns_callable(self, dispatcher):
        """create_handler returns the handle_message method."""
        handler = dispatcher.create_handler()
        assert callable(handler)
        assert handler == dispatcher.handle_message

    @pytest.mark.asyncio
    async def test_handle_message_resolves_route(self, dispatcher, sample_message):
        """handle_message resolves the route correctly."""
        with patch.object(dispatcher, "_dispatch_to_agent", new_callable=AsyncMock) as mock_dispatch:
            mock_dispatch.return_value = "Hello!"
            with patch.object(dispatcher, "_send_response", new_callable=AsyncMock):
                await dispatcher.handle_message(sample_message)

        # Check that dispatch was called
        mock_dispatch.assert_called_once()
        call_args = mock_dispatch.call_args
        route = call_args[0][1]  # Second positional arg is route

        assert route.channel_id == "telegram"
        assert route.account_id == "bot-1"
        assert route.peer_kind == "direct"

    @pytest.mark.asyncio
    async def test_handle_message_sends_response(self, dispatcher, sample_message, mock_channels):
        """handle_message sends response back to channel."""
        with patch.object(dispatcher, "_dispatch_to_agent", new_callable=AsyncMock) as mock_dispatch:
            mock_dispatch.return_value = "Hello, user!"
            await dispatcher.handle_message(sample_message)

        # Check that send was called on the channel
        mock_channel = mock_channels.get_channel.return_value
        mock_channel.send.assert_called_once()
        call_kwargs = mock_channel.send.call_args[1]
        assert call_kwargs["text"] == "Hello, user!"

    @pytest.mark.asyncio
    async def test_handle_message_error_sends_error_response(self, dispatcher, sample_message, mock_channels):
        """handle_message sends error message on exception."""
        with patch.object(dispatcher, "_dispatch_to_agent", new_callable=AsyncMock) as mock_dispatch:
            mock_dispatch.side_effect = ValueError("Test error")
            await dispatcher.handle_message(sample_message)

        # Check that error was sent
        mock_channel = mock_channels.get_channel.return_value
        mock_channel.send.assert_called_once()
        call_kwargs = mock_channel.send.call_args[1]
        assert "ValueError" in call_kwargs["text"]

    @pytest.mark.asyncio
    async def test_send_response_handles_missing_channel(self, dispatcher, mock_channels):
        """_send_response handles missing channel gracefully."""
        mock_channels.get_channel.return_value = None

        from openfang.messaging.resolver import ResolvedRoute

        route = ResolvedRoute(
            session_key="test",
            channel_id="unknown",
            account_id="bot",
            peer_id="user",
            peer_kind="direct",
            reply_target="user",
        )

        # Should not raise
        await dispatcher._send_response(route, "Hello")

    @pytest.mark.asyncio
    async def test_send_response_handles_send_failure(self, dispatcher, mock_channels):
        """_send_response handles send failure gracefully."""
        mock_channel = mock_channels.get_channel.return_value
        mock_channel.send.return_value = False

        from openfang.messaging.resolver import ResolvedRoute

        route = ResolvedRoute(
            session_key="test",
            channel_id="telegram",
            account_id="bot",
            peer_id="user",
            peer_kind="direct",
            reply_target="user",
        )

        # Should not raise
        await dispatcher._send_response(route, "Hello")


class TestChannelSetMessageHandler:
    """Test set_message_handler on channels."""

    def test_telegram_set_message_handler(self):
        """TelegramChannel accepts message handler."""
        from openfang.channels.telegram import TelegramChannel

        channel = TelegramChannel()
        handler = AsyncMock()

        channel.set_message_handler(handler)
        assert channel._message_handler is handler

        channel.set_message_handler(None)
        assert channel._message_handler is None

    def test_discord_set_message_handler(self):
        """DiscordChannel accepts message handler."""
        from openfang.channels.discord import DiscordChannel

        channel = DiscordChannel()
        handler = AsyncMock()

        channel.set_message_handler(handler)
        assert channel._message_handler is handler

    def test_stub_channels_have_set_message_handler(self):
        """All stub channels have set_message_handler method."""
        from openfang.channels import (
            GoogleChatChannel,
            IMessageChannel,
            SignalChannel,
            SlackChannel,
            WhatsAppChannel,
        )

        for ChannelClass in [WhatsAppChannel, SlackChannel, GoogleChatChannel, SignalChannel, IMessageChannel]:
            channel = ChannelClass()
            assert hasattr(channel, "set_message_handler")

            handler = AsyncMock()
            channel.set_message_handler(handler)
            assert channel._message_handler is handler


class TestChannelRegistrySetMessageHandler:
    """Test set_message_handler on registry."""

    def test_registry_sets_handler_on_all_channels(self):
        """Registry sets handler on all registered channels."""
        from openfang.channels import ChannelRegistry, DiscordChannel, TelegramChannel

        registry = ChannelRegistry()
        telegram = TelegramChannel()
        discord = DiscordChannel()

        registry.register_channel(telegram)
        registry.register_channel(discord)

        handler = AsyncMock()
        registry.set_message_handler(handler)

        assert telegram._message_handler is handler
        assert discord._message_handler is handler

    def test_registry_clears_handler(self):
        """Registry clears handler when None is passed."""
        from openfang.channels import ChannelRegistry, TelegramChannel

        registry = ChannelRegistry()
        telegram = TelegramChannel()
        registry.register_channel(telegram)

        handler = AsyncMock()
        registry.set_message_handler(handler)
        registry.set_message_handler(None)

        assert telegram._message_handler is None
