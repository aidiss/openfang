# OpenFang

Personal AI assistant infrastructure you can actually read.

A gateway connecting LLMs to your chat apps (Telegram, Discord, web) with tools, skills, and memory — in ~5K lines of Python you can understand in an afternoon.

**Fork it. Own it. Make it yours.**

## Background

Inspired by [OpenClaw](https://github.com/AbanteAI/openclaw). Borrows its core ideas — skills as markdown, protocol-based adapters, conversation routing — but implemented in Python with pydantic-ai, pydantic-settings, FastAPI, and Logfire.

## Design Principles

1. **Readable first** — Every file should be understandable without context
2. **Leverage, don't reinvent** — pydantic-ai, FastAPI, Playwright do the heavy lifting
3. **Protocols for fast tests** — In-memory fakes, not Docker, for 2-second test runs
4. **Progressive complexity** — Chat works out of the box; customization is optional

## Explicit Non-Goals

- Not production-grade (no scaling, rate limiting, enterprise auth)
- Not batteries-included — minimal defaults, you add what you need

## Who This Is For

You think in Python and want an AI assistant you can read, own, and modify.

## Usage

```bash
uv sync
cp .env.example .env        # Add your API keys
```

**Web gateway:**
```bash
uv run python -m openfang gateway
# → http://localhost:18789
```

**Interactive CLI chat:**
```bash
uv run python -m openfang chat
```

**Telegram bot:**
```bash
uv run python -m openfang telegram
```

**Scheduled tasks:**
```bash
uv run python -m openfang cron
```

## Structure

```
src/openfang/
├── agents/        # Top-level agent personas (YAML configs)
├── capabilities/  # Adapter implementations (files, memory, shell, web)
├── channels/      # Messaging platforms (Telegram, Discord)
├── gateway/       # FastAPI + HTMX templates
├── messaging/     # Message dispatch and session resolution
├── runners/       # CLI entry points
├── skills/        # Markdown skill definitions
├── subagents/     # Specialized task delegation
├── protocols.py   # Port interfaces
└── settings.py    # Configuration
```

## License

MIT
