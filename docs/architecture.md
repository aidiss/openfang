# Architecture

OpenFang follows **hexagonal architecture** (ports and adapters) to keep the core agent logic decoupled from infrastructure.

## Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Gateway                               │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │ Web UI  │  │  REST   │  │   SSE   │  │Telegram │        │
│  │ (HTMX)  │  │   API   │  │ Events  │  │ Discord │        │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │
│       │            │            │            │              │
│       └────────────┴─────┬──────┴────────────┘              │
│                          │                                   │
│                    ┌─────▼─────┐                            │
│                    │ Dispatcher │  ← Routes messages        │
│                    └─────┬─────┘                            │
│                          │                                   │
│                    ┌─────▼─────┐                            │
│                    │   Agent   │  ← pydantic-ai             │
│                    └─────┬─────┘                            │
│                          │                                   │
│    ┌─────────────────────┼─────────────────────┐           │
│    │          │          │          │          │           │
│ ┌──▼──┐  ┌───▼───┐  ┌───▼───┐  ┌───▼───┐  ┌───▼────┐     │
│ │Tools│  │Skills │  │Memory │  │Agents │  │Subagents│     │
│ └─────┘  └───────┘  └───────┘  └───────┘  └────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### Gateway (`gateway/`)

FastAPI server that handles:

- **HTTP routes** — REST API for chat, conversations, memory
- **SSE events** — Real-time streaming of agent responses
- **Web UI** — HTMX + Alpine.js dashboard
- **Channel integration** — Receives messages from Telegram/Discord

### Dispatcher (`messaging/dispatcher.py`)

Central message router:

1. Receives `InboundMessage` from any channel
2. Resolves session key via `Resolver`
3. Loads or creates conversation
4. Runs agent with appropriate context
5. Sends response back to originating channel

### Agent (`agent.py`)

pydantic-ai agent factory with:

- **Dynamic tools** — Filtered by user permissions
- **System prompt** — Built from skills + memory
- **Streaming** — Real-time response chunks

### Deps (`deps.py`)

Dependency injection container bundling all adapters:

```python
@dataclass
class Deps:
    user: User
    storage: StorageAdapters      # files, memory, conversations
    web_adapters: WebAdapters     # web browsing
    workspace: WorkspaceAdapters  # shell, projects
    scheduling: SchedulingAdapters # cron jobs
    comms: CommsAdapters          # channels, skills
```

## Ports and Adapters

### Ports (`protocols.py`)

Protocol interfaces define contracts:

```python
class Files(Protocol):
    def read(self, path: str) -> str: ...
    def write(self, path: str, content: str) -> None: ...
    def list_dir(self, path: str) -> list[str]: ...

class Memory(Protocol):
    async def remember(self, fact: str) -> None: ...
    async def recall(self, query: str) -> list[str]: ...
    async def forget(self, fact_id: str) -> None: ...
```

### Adapters (`capabilities/`)

Concrete implementations:

| Port | Adapter | Description |
|------|---------|-------------|
| `Files` | `LocalFiles` | Local filesystem access |
| `Memory` | `InMemoryMemory` | In-memory fact storage |
| `Web` | `PlaywrightWeb` | Browser automation |
| `Shell` | `LocalShell` | Command execution |
| `Conversations` | `InMemoryConversations` | Chat history |
| `Channel` | `TelegramChannel` | Telegram Bot API |
| `Channel` | `DiscordChannel` | Discord bot |

## Agents & Subagents

### Top-Level Agents (`agents/`)

Agent personas defined in YAML with:
- **Identity** — name, emoji
- **Tool policies** — allow/deny lists
- **Skill allowlists** — which skills are available
- **Subagent permissions** — which subagents can be spawned

### Subagents (`subagents/`)

Specialized task delegation system:
- **code_analyzer** — Code review and analysis
- **web_researcher** — Web research tasks
- **summarizer** — Content summarization

Subagents run with limited tools and return results inline to the parent agent.

## Message Flow

```
User (Telegram)
     │
     ▼
TelegramChannel.on_message()
     │
     ▼
InboundMessage { channel, peer, text, ... }
     │
     ▼
Dispatcher.dispatch()
     │
     ├─► Resolver.resolve() → session_key
     │
     ├─► Conversations.get_or_create()
     │
     ├─► Agent.run(message, deps)
     │      │
     │      ├─► Tools (file_read, web_fetch, ...)
     │      ├─► Skills (injected prompts)
     │      └─► Memory (recall context)
     │
     └─► Channel.send_message(response)
              │
              ▼
         User (Telegram)
```

## Tool Permission System

Tools are gated by user roles:

```python
TOOL_PERMISSIONS: dict[str, set[str] | None] = {
    "shell_exec": {"admin"},           # Admin only
    "file_write": {"admin", "developer"},
    "web_fetch": None,                 # All users
}
```

The agent factory filters tools based on `user.roles` before creating the agent.

## Testing Philosophy

**Fakes over Mocks** — Adapters have in-memory implementations that behave like real ones:

- `InMemoryMemory` — Stores facts in a dict
- `InMemoryConversations` — Stores messages in memory
- `FakeShell` — Returns predefined command outputs
- `FakeWeb` — Returns predefined page content

This makes tests fast, deterministic, and realistic.

## Key Files

| File | Purpose |
|------|---------|
| [`protocols.py`](https://github.com/aidiss/openfang/blob/main/src/openfang/protocols.py) | All port definitions |
| [`deps.py`](https://github.com/aidiss/openfang/blob/main/src/openfang/deps.py) | DI container |
| [`tools.py`](https://github.com/aidiss/openfang/blob/main/src/openfang/tools.py) | ~40 agent tools |
| [`agent.py`](https://github.com/aidiss/openfang/blob/main/src/openfang/agent.py) | Agent factory + permissions |
| [`messaging/dispatcher.py`](https://github.com/aidiss/openfang/blob/main/src/openfang/messaging/dispatcher.py) | Message routing |
| [`agents/`](https://github.com/aidiss/openfang/blob/main/src/openfang/agents/) | Top-level agent configs |
| [`subagents/`](https://github.com/aidiss/openfang/blob/main/src/openfang/subagents/) | Task delegation system |
