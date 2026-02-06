# OpenFang

A multi-channel AI agent gateway. Connect one agent to Telegram, Discord, web, or CLI.

## Background

Inspired by [OpenClaw](https://github.com/AbanteAI/openclaw). Borrows its core ideas — skills as markdown, protocol-based adapters, conversation routing — but implemented in Python with pydantic-ai, pydantic-settings, FastAPI, and Logfire.

## Design

**Priorities:** Readability first, then maintainability, then extendability.

- **Hexagonal architecture** — Protocols define ports; adapters implement them
- **Pydantic everywhere** — Validation, settings, AI agents, API schemas
- **Async-first** — Native async throughout
- **No-build frontend** — HTMX + Tailwind via CDN, server returns HTML fragments
- **Fakes over mocks** — InMemory adapters for tests behave like real implementations
- **Observable by default** — Logfire spans on all operations
- **Skills as markdown** — Capabilities defined in plain text files

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
├── adapters/      # Implementations (files, memory, shell, channels, skills)
├── gateway/       # FastAPI + HTMX templates
├── routing/       # Message dispatch and session resolution
├── runners/       # CLI entry points
├── protocols.py   # Port interfaces
└── settings.py    # Configuration
```

## License

MIT
