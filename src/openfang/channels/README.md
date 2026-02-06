# Channels

External messaging platform connectors. Each channel handles authentication, receiving inbound messages, and sending responses.

**Implemented:** Telegram, Discord
**Stubs:** WhatsApp, Slack, Signal, Google Chat, iMessage

Key files:
- `registry.py` - Manages multiple channels and accounts
- `models.py` - `InboundMessage`, `ChannelAccount`, `ChannelStatus`
- `telegram.py` - Reference implementation using python-telegram-bot
