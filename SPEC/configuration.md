# Configuration

Settings and environment variables for OpenFang.

## Overview

Configuration uses `pydantic-settings` with:
- Environment variables prefixed with `OPENFANG_`
- `.env` file support
- Type validation and defaults

Location: `src/openfang/settings.py`

## Settings Class

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="OPENFANG_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Gateway server
    host: str = "127.0.0.1"
    port: int = 18789

    # LLM Model
    model: str = "openai:gpt-4o"

    # Heartbeat
    heartbeat_enabled: bool = True
    heartbeat_interval: int = 1800
    heartbeat_prompt: str = "Check HEARTBEAT.md..."
    heartbeat_ack_token: str = "HEARTBEAT_OK"
    heartbeat_ack_max_len: int = 300

    # Logfire
    logfire_enabled: bool = True
    logfire_service_name: str = "openfang-gateway"

    # Channel tokens
    telegram_bot_token: str | None = None
    discord_bot_token: str | None = None

    # Webhooks
    webhooks_enabled: bool = False
    webhooks_token: str | None = None

    # CLI user identity
    user_email: str = "cli@local"
    user_phone: str | None = None
    user_telegram: str | None = None
```

## Environment Variables

### Gateway

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENFANG_HOST` | `127.0.0.1` | Server bind address |
| `OPENFANG_PORT` | `18789` | Server port |

### LLM

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENFANG_MODEL` | `openai:gpt-4o` | Model string |
| `PYDANTIC_AI_GATEWAY_API_KEY` | — | If set, prefixes model with `gateway/` |

Model format: `provider:model` (e.g., `openai:gpt-4o`, `anthropic:claude-sonnet-4-20250514`)

### Heartbeat

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENFANG_HEARTBEAT_ENABLED` | `true` | Enable heartbeat loop |
| `OPENFANG_HEARTBEAT_INTERVAL` | `1800` | Interval in seconds (30 min) |
| `OPENFANG_HEARTBEAT_PROMPT` | `"Check HEARTBEAT.md..."` | Prompt sent to agent |
| `OPENFANG_HEARTBEAT_ACK_TOKEN` | `HEARTBEAT_OK` | Expected response |
| `OPENFANG_HEARTBEAT_ACK_MAX_LEN` | `300` | Max response length to check |

### Observability

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENFANG_LOGFIRE_ENABLED` | `true` | Enable Logfire tracing |
| `OPENFANG_LOGFIRE_SERVICE_NAME` | `openfang-gateway` | Service name in traces |

### Channels

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENFANG_TELEGRAM_BOT_TOKEN` | — | Telegram bot token |
| `OPENFANG_DISCORD_BOT_TOKEN` | — | Discord bot token |

Channels auto-configure when tokens are set.

### Webhooks

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENFANG_WEBHOOKS_ENABLED` | `false` | Enable webhook endpoints |
| `OPENFANG_WEBHOOKS_TOKEN` | — | Auth token for webhooks |

### User Identity

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENFANG_USER_EMAIL` | `cli@local` | Default user email |
| `OPENFANG_USER_PHONE` | — | User phone number |
| `OPENFANG_USER_TELEGRAM` | — | User Telegram ID |

## .env File

Create `.env` in the project root:

```bash
# LLM
OPENFANG_MODEL=anthropic:claude-sonnet-4-20250514
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Or use pydantic-ai gateway
PYDANTIC_AI_GATEWAY_API_KEY=your-gateway-key

# Channels
OPENFANG_TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
OPENFANG_DISCORD_BOT_TOKEN=MTIz...

# Gateway
OPENFANG_HOST=0.0.0.0
OPENFANG_PORT=8080

# Heartbeat
OPENFANG_HEARTBEAT_ENABLED=true
OPENFANG_HEARTBEAT_INTERVAL=3600

# Observability
OPENFANG_LOGFIRE_ENABLED=false
```

## Model Resolution

The `get_model()` method handles gateway prefixing:

```python
def get_model(self) -> str:
    model = self.model

    # If gateway key is set, add prefix
    if os.environ.get("PYDANTIC_AI_GATEWAY_API_KEY"):
        if not model.startswith("gateway/"):
            return f"gateway/{model}"

    return model
```

Examples:
- No gateway key: `openai:gpt-4o` → `openai:gpt-4o`
- With gateway key: `openai:gpt-4o` → `gateway/openai:gpt-4o`

## Singleton Access

```python
from openfang.settings import settings

# Use settings anywhere
model = settings.get_model()
port = settings.port
```

## Source Files

- [settings.py](../src/openfang/settings.py) - Settings class
- [.env.example](../.env.example) - Example configuration

---

## OpenClaw Reference

### Key Files

- `/openclaw/src/config/` - Configuration modules
- `/openclaw/src/config/sessions.ts` - Session scope config
- `/openclaw/src/agents/defaults.ts` - Default model/provider

### OpenClaw's Approach

**Multi-Layer Configuration**:
- Agent-level config (YAML files per agent)
- Channel-level config (per platform settings)
- Session-level config (scope modes, storage)
- Environment variables for secrets

**Session Configuration** (from `openclaw-patterns.md`):
- Scope modes: global, per-sender, per-channel-peer
- File-based store with atomic writes
- Metadata: updatedAt, createdAt, lastHeartbeatText

**Model Defaults**:
- Default provider: `anthropic`
- Default model: `claude-opus-4-5`
- Default context: 200k tokens
- Model metadata lazy-loaded from registry

### Diff: OpenFang vs OpenClaw

| Aspect | OpenFang | OpenClaw |
|--------|----------|----------|
| **Config system** | pydantic-settings | Custom config loader |
| **File format** | `.env` + env vars | YAML + env vars |
| **Validation** | Pydantic types | TypeScript types |
| **Hot reload** | Not implemented | Config reload triggers UI updates |
| **Multi-agent** | Single settings | Per-agent config files |

### Shared Patterns

Both projects:
- Use environment variables for secrets
- Support `.env` files
- Have sensible defaults
- Auto-configure based on available tokens
