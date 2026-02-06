# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**OpenFang** - Lightweight AI agent gateway inspired by OpenClaw. Python 3.13+, Pydantic ecosystem.

## Commands

```bash
uv sync --all-extras                       # Install all deps
uv run pre-commit install                  # Setup git hooks (once)
uv run python -m openfang gateway          # Run gateway (localhost:18789)
uv run python -m openfang chat             # Interactive chat
uv run pytest --cov                        # Run tests with coverage
uv run pytest tests/test_tools.py -k memory  # Run single test
uv run ruff check . && uv run ruff format . # Lint & format
uv run ty check                            # Type check
uv run mkdocs serve                        # Docs preview
```

## Architecture

### Hexagonal (Ports & Adapters)

- **Ports** ([protocols.py](src/openfang/protocols.py)): Protocol interfaces define contracts (`Files`, `Web`, `Memory`, `Shell`, `Channels`, `Skills`, etc.)
- **Adapters** ([adapters/](src/openfang/adapters/)): Concrete implementations (`LocalFiles`, `PlaywrightWeb`, `InMemoryMemory`, `TelegramChannel`, etc.)
- **Deps** ([deps.py](src/openfang/deps.py)): Dependency container bundles all adapters + user context, passed to agent

### Agent & Tools

- **Agent Factory** ([agent.py](src/openfang/agent.py)): Creates pydantic-ai Agent with tools and dynamic instructions
- **Tool Permissions**: `TOOL_PERMISSIONS` dict maps tool names to required roles (`admin`, `developer`, or `None` for all users)
- **Tools** ([tools.py](src/openfang/tools.py)): All tool functions in `ALL_TOOLS` list; use `@tool_errors` decorator for consistent error handling

### Message Routing

- **Dispatcher** ([routing/dispatcher.py](src/openfang/routing/dispatcher.py)): Central router - receives channel messages, runs agent, sends responses
- **Resolver** ([routing/resolver.py](src/openfang/routing/resolver.py)): Maps inbound messages to session keys: `{channel}:{account}:{peer_kind}:{peer_id}`
- **Channels** ([adapters/channels/](src/openfang/adapters/channels/)): Platform connectors (Telegram, Discord implemented; others stubbed)

### Testing Philosophy

Tests use **Fakes over Mocks** - `InMemory*` adapters work like real implementations but in memory. See [conftest.py](tests/conftest.py) for `FakeWeb`, `FakeShell`, `FakeProjects`, etc.

## Key Rules

- `/openclaw/` is reference only. Do NOT modify.
- Config via env vars with `OPENFANG_` prefix or `.env` file
- Async-first, type-first, Pydantic everywhere
