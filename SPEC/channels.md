# Channels System

Messaging platform connectors that receive and send messages to external services.

## Purpose

Channels provide bidirectional communication with messaging platforms:
- **Inbound**: Receive messages from Telegram, Discord, etc.
- **Outbound**: Send responses back to users
- **Multi-account**: Support multiple bot accounts per platform

## Message Flow

```
User sends message
        │
        ▼
┌───────────────┐
│   Channel     │  (TelegramChannel, DiscordChannel)
│   listener    │
└───────┬───────┘
        │ InboundMessage
        ▼
┌───────────────┐
│  Dispatcher   │  (MessageDispatcher.handle)
└───────┬───────┘
        │
        ▼
┌───────────────┐
│   Resolver    │  → session key: "telegram:default:direct:123456"
└───────┬───────┘
        │
        ▼
┌───────────────┐
│    Agent      │  (create_agent, tools, instructions)
└───────┬───────┘
        │
        ▼
┌───────────────┐
│   Channel     │  → send response
│   .send()     │
└───────────────┘
```

## Data Models

### InboundMessage

```python
class InboundMessage(BaseModel):
    channel_id: str           # "telegram", "discord"
    account_id: str           # "default", "work-bot"
    sender_id: str            # User ID on the platform
    sender_name: str | None
    target_id: str            # Chat/group/channel ID
    text: str
    reply_to_id: str | None
    chat_type: Literal["direct", "group", "channel"]
    timestamp: datetime
```

### ChannelAccount

```python
class ChannelAccount(BaseModel):
    id: str                   # "default", "work-bot"
    channel_id: str           # "telegram", "discord"
    name: str | None
    enabled: bool
    config: dict[str, Any]    # {"token": "..."}
```

### ChannelStatus

```python
class ChannelStatus(BaseModel):
    account_id: str
    channel_id: str
    name: str | None
    running: bool
    connected: bool
    last_inbound_at: datetime | None
    last_outbound_at: datetime | None
    last_error: str | None
```

### ChannelInfo

```python
class ChannelInfo(BaseModel):
    id: str                   # "telegram"
    name: str                 # "Telegram"
    emoji: str                # "📱"
    description: str
    config_fields: list[str]  # ["token"]
```

## Protocol: Channel

```python
@runtime_checkable
class Channel(Protocol):
    id: str  # "telegram", "discord"

    async def start(self, account_id: str) -> None:
        """Start the channel for an account."""

    async def stop(self, account_id: str) -> None:
        """Stop the channel for an account."""

    async def send(self, account_id: str, target: str, text: str) -> bool:
        """Send a message. Returns True on success."""

    async def status(self, account_id: str) -> ChannelStatus:
        """Get the status of an account."""

    def info(self) -> ChannelInfo:
        """Get channel metadata."""

    def set_message_handler(self, handler: MessageHandler | None) -> None:
        """Set callback for inbound messages."""
```

## Protocol: Channels (Registry)

```python
@runtime_checkable
class Channels(Protocol):
    def get_channel(self, channel_id: str) -> Channel | None:
    def list_channels(self) -> list[ChannelInfo]:
    async def add_account(self, account: ChannelAccount) -> None:
    async def remove_account(self, channel_id: str, account_id: str) -> None:
    async def list_accounts(self, channel_id: str | None = None) -> list[ChannelAccount]:
    async def start_account(self, channel_id: str, account_id: str) -> None:
    async def stop_account(self, channel_id: str, account_id: str) -> None:
    async def start_all(self) -> None:
    async def stop_all(self) -> None:
    async def status(self) -> list[ChannelStatus]:
    def set_message_handler(self, handler: MessageHandler | None) -> None:
```

## Session Keys

The **Resolver** creates unique session keys for conversation isolation:

```
{channel_id}:{account_id}:{peer_kind}:{peer_id}
```

Examples:
- `telegram:default:direct:123456` - DM with user 123456
- `telegram:default:group:789` - Group chat 789
- `discord:work:direct:user_id` - Discord DM

`peer_kind` = "direct" | "group" | "channel"

## Implemented Channels

### Telegram

Location: `src/openfang/channels/telegram.py`

- Uses `python-telegram-bot` library
- Config: `token`
- Supports: DMs, groups, channels

### Discord

Location: `src/openfang/channels/discord.py`

- Uses `discord.py` library
- Config: `token`
- Supports: DMs, server channels

## Stubbed Channels

Interfaces defined, implementations pending:

| Channel | File | Status |
|---------|------|--------|
| Slack | `slack.py` | Stubbed |
| WhatsApp | `whatsapp.py` | Stubbed |
| Google Chat | `googlechat.py` | Stubbed |
| Signal | `signal.py` | Stubbed |
| iMessage | `imessage.py` | Stubbed |

## Tools

| Tool | Args | Description |
|------|------|-------------|
| `telegram_send` | `chat_id`, `message` | Send via Telegram |
| `discord_send` | `channel_id`, `message` | Send via Discord |

## Configuration

Via environment variables:

```bash
OPENFANG_TELEGRAM_BOT_TOKEN=123:ABC...
OPENFANG_DISCORD_BOT_TOKEN=MTIz...
```

Channels auto-configure when tokens are set.

## Implementing a New Channel

1. Create `src/openfang/channels/newchannel.py`
2. Implement `Channel` protocol
3. Register in `ChannelRegistry.default()`
4. Add config fields to settings

```python
class NewChannel:
    id = "newchannel"

    def __init__(self):
        self._accounts: dict[str, AccountState] = {}
        self._handler: MessageHandler | None = None

    async def start(self, account_id: str) -> None:
        # Connect to service, start listener
        pass

    async def send(self, account_id: str, target: str, text: str) -> bool:
        # Send message via platform API
        return True

    def set_message_handler(self, handler: MessageHandler | None) -> None:
        self._handler = handler

    # When message received:
    # await self._handler(InboundMessage(...))
```

## Source Files

- [channels/models.py](../src/openfang/channels/models.py) - Data models
- [channels/registry.py](../src/openfang/channels/registry.py) - ChannelRegistry
- [channels/telegram.py](../src/openfang/channels/telegram.py) - Telegram
- [channels/discord.py](../src/openfang/channels/discord.py) - Discord
- [messaging/dispatcher.py](../src/openfang/messaging/dispatcher.py) - Message routing
- [messaging/resolver.py](../src/openfang/messaging/resolver.py) - Session keys
- [protocols.py:251-336](../src/openfang/protocols.py) - Channel protocols

---

## OpenClaw Reference

### Key Files

- `/openclaw/src/channels/registry.ts` - Channel registry and metadata
- `/openclaw/src/channels/plugins/index.ts` - Plugin channel loading
- `/openclaw/src/telegram/`, `/discord/`, `/slack/` - Core implementations
- `/openclaw/src/infra/dedupe.ts` - Message deduplication
- `/openclaw/extensions/` - Extension channels (msteams, matrix, zalo)

### OpenClaw's Approach

**Channel Registry Pattern**:
- Central registry maps channel IDs to metadata
- Declared in `CHAT_CHANNEL_ORDER` for consistent ordering
- Aliases supported (e.g., `imsg` → `imessage`)
- No eager loading of implementations

**Plugin-Based Architecture**:
- Core channels bundled (Telegram, Discord, Slack, Signal, iMessage, WhatsApp)
- Extension channels loaded via plugin system
- Each plugin can have own dependencies

**Multi-Layer Gating**:
- **Command gating**: Which commands allowed per channel/user
- **Allowlists**: User/group allowlists per channel
- **Mention gating**: Bot mention requirement (configurable)
- **Tool permissions**: Channel-aware tool access

**Message Deduplication** (from `openclaw-patterns.md`):
- TTL-based cache (20 minutes default, 5000 items max)
- Composite key: `provider|accountId|sessionKey|peerId|threadId|messageId`
- Prevents duplicate processing from webhook retries

**Conversation Locking**:
- Promise chaining serializes per-conversation
- Message queueing during streaming
- Inbound debouncing: buffer rapid messages, flush together

**Message Chunking**:
- Platform-specific limits (Telegram: 4096 text, 1024 caption)
- Markdown-aware splitting (don't break code fences)
- Re-open fenced blocks after split

### Diff: OpenFang vs OpenClaw

| Aspect | OpenFang | OpenClaw |
|--------|----------|----------|
| **Registry** | Simple dict | Metadata + aliases + ordering |
| **Plugins** | Not implemented | Full plugin system |
| **Deduplication** | Not implemented | TTL cache with composite keys |
| **Conversation lock** | Not implemented | Promise chaining + queueing |
| **Message chunking** | Not implemented | Markdown-aware splitting |
| **Gating layers** | Role-based only | Command + allowlist + mention + tool |
| **Implemented** | Telegram, Discord | TG, Discord, Slack, Signal, iMessage, WhatsApp + extensions |

### Future Enhancement Ideas

From OpenClaw patterns:
- Add message deduplication cache
- Implement conversation locking for concurrent messages
- Add markdown-aware message chunking
- Multi-layer gating (allowlists, mention requirements)
- Plugin system for extension channels
