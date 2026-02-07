# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**OpenFang** - Lightweight AI agent gateway inspired by OpenClaw. Python 3.13+, Pydantic ecosystem.

See [README.md](README.md) for design philosophy and principles.

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
- **Adapters** ([capabilities/](src/openfang/capabilities/)): Concrete implementations (`LocalFiles`, `PlaywrightWeb`, `InMemoryMemory`, etc.)
- **Deps** ([deps.py](src/openfang/deps.py)): Dependency container bundles all adapters + user context, passed to agent

### Agent & Tools

- **Agent Factory** ([agent.py](src/openfang/agent.py)): Creates pydantic-ai Agent with tools and dynamic instructions
- **Tool Permissions**: `TOOL_PERMISSIONS` dict maps tool names to required roles (`admin`, `developer`, or `None` for all users)
- **Tools** ([tools.py](src/openfang/tools.py)): All tool functions in `ALL_TOOLS` list; use `@tool_errors` decorator for consistent error handling

### Agents & Subagents

- **Agents** ([agents/](src/openfang/agents/)): Top-level agent personas defined in YAML (identity, tool policies, skill allowlists)
- **Subagents** ([subagents/](src/openfang/subagents/)): Specialized task delegation (code_analyzer, web_researcher, summarizer)

### Message Routing

- **Dispatcher** ([messaging/dispatcher.py](src/openfang/messaging/dispatcher.py)): Central router - receives channel messages, runs agent, sends responses
- **Resolver** ([messaging/resolver.py](src/openfang/messaging/resolver.py)): Maps inbound messages to session keys: `{channel}:{account}:{peer_kind}:{peer_id}`
- **Channels** ([channels/](src/openfang/channels/)): Platform connectors (Telegram, Discord implemented; others stubbed)

### Gateway

- **Gateway** ([gateway/core.py](src/openfang/gateway/core.py)): HTTP server + Web UI + channels in one process
- **Why "gateway"**: CLI similarity with OpenClaw (`openfang gateway` mirrors `openclaw gateway`)
- **What it runs**: HTTP API, Web UI (HTMX), SSE events, all configured channels, heartbeat
- **Key difference from OpenClaw**: OpenClaw's gateway is WebSocket RPC for native apps; ours is HTTP REST + SSE
- **Single command**: `openfang gateway` starts everything (HTTP + Telegram + Discord + heartbeat)

### Testing Philosophy

Tests use **Fakes over Mocks** - `InMemory*` adapters work like real implementations but in memory. See [conftest.py](tests/conftest.py) for `FakeWeb`, `FakeShell`, `FakeProjects`, etc.

## Specifications (SPEC/)

The [SPEC/](SPEC/) folder contains **specification files** that define contracts, data models, and interfaces. Specs are the source of truth - read them before implementing features.

**When to use specs:**
- Before implementing a new feature, read the relevant spec
- When adding adapters (e.g., Redis memory, Slack channel), consult the spec for expected behavior
- For understanding system boundaries and protocols

**Key specs:**
| Spec | What it defines |
|------|-----------------|
| [OVERVIEW.md](SPEC/OVERVIEW.md) | Architecture, request flow, hexagonal design |
| [protocols.md](SPEC/protocols.md) | All protocol interfaces (`Files`, `Web`, `Memory`, etc.) |
| [tools.md](SPEC/tools.md) | Agent tools, permissions, categories |
| [channels.md](SPEC/channels.md) | Message routing, channel protocol, session keys |
| [configuration.md](SPEC/configuration.md) | All `OPENFANG_*` settings |

Each spec includes: purpose, protocol interface, data models, current implementation, extension points, and OpenClaw reference.

## Key Rules

- `/openclaw/` is reference only. Do NOT modify.
- Config via env vars with `OPENFANG_` prefix or `.env` file
- Async-first, type-first, Pydantic everywhere

@AGENTS.md
