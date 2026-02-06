"""OpenFang channels - platform connectors for external messaging."""

from .discord import DiscordChannel
from .googlechat import GoogleChatChannel
from .imessage import IMessageChannel
from .models import ChannelAccount, ChannelInfo, ChannelStatus, InboundMessage
from .registry import ChannelRegistry
from .signal import SignalChannel
from .slack import SlackChannel
from .telegram import TelegramChannel
from .whatsapp import WhatsAppChannel

__all__ = [
    "ChannelAccount",
    "ChannelInfo",
    "ChannelStatus",
    "InboundMessage",
    "ChannelRegistry",
    # Implemented
    "DiscordChannel",
    "TelegramChannel",
    # Stubs (not implemented)
    "GoogleChatChannel",
    "IMessageChannel",
    "SignalChannel",
    "SlackChannel",
    "WhatsAppChannel",
]
