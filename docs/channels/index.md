# Channels

Channels connect OpenFang to messaging platforms. One assistant, all your chats.

## Supported Channels

| Channel | Status | Notes |
|---------|--------|-------|
| **[Telegram](telegram.md)** | :material-check-circle:{ .green } Ready | Bot API via python-telegram-bot |
| **[Discord](discord.md)** | :material-check-circle:{ .green } Ready | Slash commands + DMs |
| **WhatsApp** | :material-clock-outline: Planned | Coming soon |
| **Slack** | :material-clock-outline: Planned | Coming soon |
| **Signal** | :material-clock-outline: Planned | Coming soon |
| **iMessage** | :material-clock-outline: Planned | macOS only |

## How Channels Work

1. **Receive** — Channel adapter receives message from platform
2. **Normalize** — Convert to `InboundMessage` (unified format)
3. **Route** — Dispatcher routes to agent with session context
4. **Respond** — Agent response sent back via same channel

```python
@dataclass
class InboundMessage:
    channel: str           # "telegram", "discord", etc.
    account: str           # Bot account identifier
    peer_kind: str         # "user" or "group"
    peer_id: str           # User/group ID
    sender_id: str         # Who sent the message
    sender_name: str       # Display name
    text: str              # Message content
    timestamp: datetime
```

## Session Isolation

Each channel + peer combination gets its own session:

- `telegram:default:user:12345` — DM with user 12345
- `telegram:default:group:67890` — Group chat
- `discord:default:user:abc123` — Discord DM

This means:
- DM conversations are private per user
- Group chats have shared context
- Cross-channel context is NOT shared

## Quick Setup

### Telegram

```bash
# 1. Get token from @BotFather
# 2. Add to .env
OPENFANG_TELEGRAM_BOT_TOKEN=123456:ABC-xyz

# 3. Start gateway
uv run openfang gateway
```

[Full Telegram guide →](telegram.md)

### Discord

```bash
# 1. Create app at discord.com/developers
# 2. Add to .env
OPENFANG_DISCORD_BOT_TOKEN=your-token

# 3. Start gateway
uv run openfang gateway
```

[Full Discord guide →](discord.md)

## Adding New Channels

Channels implement the `Channel` protocol:

```python
class Channel(Protocol):
    @property
    def id(self) -> str: ...

    def configure_account(self, account_id: str, token: str) -> None: ...

    async def start(self) -> None: ...

    async def stop(self) -> None: ...

    async def send_message(
        self,
        account: str,
        peer_kind: str,
        peer_id: str,
        text: str,
    ) -> None: ...

    def set_message_handler(
        self,
        handler: Callable[[InboundMessage], Awaitable[None]] | None,
    ) -> None: ...
```

See [TelegramChannel](https://github.com/aidiss/openfang/blob/main/src/openfang/adapters/channels/telegram.py) for a reference implementation.
