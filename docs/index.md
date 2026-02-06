# OpenFang

Lightweight AI agent gateway. Connect LLMs to channels (Telegram, Discord) with tools, skills, and conversation memory.

## Features

- **Channels** - Telegram, Discord (more coming)
- **Tools** - Files, shell, web browsing, memory, cron
- **Skills** - Markdown-defined capabilities (GitHub, weather, etc.)
- **Gateway** - FastAPI server with web UI and REST API

## Quick Start

```bash
# Install
uv sync

# Run gateway (localhost:18789)
uv run openfang gateway

# Or interactive CLI
uv run openfang chat
```

## Configuration

Environment variables (or `.env` file):

```bash
OPENFANG_TELEGRAM_BOT_TOKEN=your-token  # Enable Telegram
OPENFANG_DISCORD_BOT_TOKEN=your-token   # Enable Discord
OPENFANG_HOST=0.0.0.0                   # Bind address
OPENFANG_PORT=18789                     # Port
```

## Architecture

```
src/openfang/
├── capabilities/   # Adapter implementations (files, memory, web, shell)
├── channels/       # Platform connectors (Telegram, Discord, etc.)
├── skills/         # Markdown skill definitions
├── messaging/      # Message routing (dispatcher, resolver)
├── gateway/        # FastAPI HTTP server + web UI
├── runners/        # Entry points (CLI, gateway, telegram, cron)
├── protocols.py    # Port interfaces
├── deps.py         # Dependency injection container
├── agent.py        # pydantic-ai agent factory
├── tools.py        # All agent tools
└── chat.py         # Conversation management
```

## Next Steps

- [API Reference](api.md) - Auto-generated from docstrings
