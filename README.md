# OpenFang

Lightweight AI agent gateway inspired by OpenClaw. Minimal code, maximum capability.

## Quick Start

```bash
# Install dependencies
uv sync

# Run the gateway
uv run python -m openfang gateway

# Open http://localhost:18789
```

## Configuration

Settings via environment variables (prefix `OPENFANG_`) or `.env` file:

```bash
OPENFANG_HOST=0.0.0.0
OPENFANG_PORT=8080
OPENFANG_HEARTBEAT_ENABLED=true
OPENFANG_HEARTBEAT_INTERVAL=1800
OPENFANG_LOGFIRE_ENABLED=true
```

## Core Principles

### Foundation
- **OpenClaw-inspired** - Lightweight implementation of key OpenClaw features
- **Python 3.13+** - Modern Python, leveraging latest features
- **Type-first** - Full type hints, runtime validation via Pydantic

### Pydantic Universe
- **pydantic** - Data validation and serialization
- **pydantic-ai** - AI agent framework
- **pydantic-settings** - Configuration management
- **FastAPI** - Web framework built on Pydantic
- **Logfire** - Observability with auto-instrumentation

### Architecture
- **Protocol-based abstractions** - Files, Memory, Shell, Web, Cron, Conversations as protocols
- **Dependency injection** - Deps container for clean composition
- **Async-first** - Native async throughout
- **Observable by default** - Logfire spans for all operations

### Frontend
- **No-build UI** - HTMX + Alpine.js + Tailwind via CDN
- **HTML-over-the-wire** - Server returns HTML fragments
- **Progressive enhancement** - Works without JS where possible

### Security
- **Capability-based** - Explicit permissions per operation
- **User context everywhere** - All operations scoped to user
- **Conversation isolation** - State contained per conversation

### Extensibility
- **Swappable backends** - InMemory for dev, real implementations for prod
- **Skill compatibility** - Same skill interface as OpenClaw
- **Plugin-friendly** - Clean extension points

### Philosophy
- **Minimal viable** - Only what's needed, no more
- **Readable over clever** - Clear code over clever abstractions
- **Batteries included but removable** - Sensible defaults, easy to swap

## Project Structure

```
src/openfang/
├── capabilities/     # Protocol implementations (Files, Memory, Shell, etc.)
├── gateway/          # FastAPI app + HTMX templates
│   └── templates/    # Jinja2 templates
├── runners/          # CLI commands (gateway, chat, telegram, cron)
├── agent.py          # Pydantic-AI agent definition
├── chat.py           # Chat handling with logfire spans
├── deps.py           # Dependency injection container
├── models.py         # Pydantic models
└── settings.py       # Pydantic-settings configuration
```

## CLI Commands

```bash
# Interactive chat
uv run python -m openfang chat

# Single prompt
uv run python -m openfang run "What files are in the project?"

# Gateway server
uv run python -m openfang gateway --port 8080

# Telegram bot
uv run python -m openfang telegram --token $TELEGRAM_BOT_TOKEN

# Cron checker
uv run python -m openfang cron --interval 60
```

## License

MIT
