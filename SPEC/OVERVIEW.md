# Architecture Overview

OpenFang is a personal AI assistant gateway built on **hexagonal architecture** (ports and adapters).

## Core Concepts

### Hexagonal Architecture

```
                    ┌─────────────────────────────────────┐
                    │           APPLICATION               │
     Inbound        │                                     │        Outbound
    ─────────►      │   ┌─────────┐     ┌─────────┐      │      ─────────►
    Channels        │   │  Agent  │────►│  Tools  │      │        Files
    HTTP API        │   └────┬────┘     └────┬────┘      │        Web
    CLI             │        │               │           │        Memory
                    │        ▼               ▼           │        Shell
                    │   ┌─────────────────────────┐      │        Channels
                    │   │         Deps            │      │
                    │   │  (adapter container)    │      │
                    │   └─────────────────────────┘      │
                    └─────────────────────────────────────┘
```

**Ports** = Protocol interfaces in `protocols.py`
**Adapters** = Implementations in `capabilities/` and `channels/`

### Request Flow

```
User Message
    │
    ▼
┌──────────┐    ┌────────────┐    ┌─────────┐    ┌──────────┐
│ Channel  │───►│ Dispatcher │───►│  Agent  │───►│ Response │
│ (TG/Web) │    │            │    │         │    │          │
└──────────┘    └────────────┘    └─────────┘    └──────────┘
                      │                │
                      ▼                ▼
                 ┌─────────┐     ┌─────────┐
                 │ Resolver│     │  Tools  │
                 │(session)│     │         │
                 └─────────┘     └─────────┘
```

1. **Channel** receives message (Telegram, Discord, Web UI)
2. **Dispatcher** routes to agent, creates Deps container
3. **Resolver** creates session key: `{channel}:{account}:{peer_kind}:{peer_id}`
4. **Agent** processes with tools, returns response
5. **Channel** sends response back

### Deps Container

`Deps` bundles all adapters for an agent execution:

```python
@dataclass
class Deps:
    user: User
    storage: StorageAdapters      # files, memory, conversations
    web_adapters: WebAdapters     # web, sessions
    workspace: WorkspaceAdapters  # shell, projects
    scheduling: SchedulingAdapters # cron
    comms: CommsAdapters          # channels, skills

    # Context
    current_page: str | None
    conversation_id: str | None

    # Subagent
    is_subagent: bool
    subagents: SubagentRegistry | None
    subagent_executor: SubagentExecutor | None
```

Created per-request via `create_deps()` async context manager.

## Directory Structure

```
src/openfang/
├── agents/         # Agent personas (YAML configs)
├── capabilities/   # Adapter implementations
│   ├── files.py      LocalFiles
│   ├── memory.py     InMemoryMemory
│   ├── shell.py      LocalShell
│   ├── web.py        PlaywrightWeb
│   └── ...
├── channels/       # Platform connectors
│   ├── telegram.py   TelegramChannel
│   ├── discord.py    DiscordChannel
│   └── ...
├── gateway/        # HTTP server + Web UI
│   ├── app.py        FastAPI app
│   ├── routes/       API endpoints
│   └── templates/    HTMX templates
├── messaging/      # Message routing
│   ├── dispatcher.py
│   └── resolver.py
├── skills/         # Skill system
│   ├── models.py     Skill, SkillMetadata
│   ├── registry.py   SkillRegistry
│   └── bundled/      Built-in skills
├── subagents/      # Task delegation
│   ├── models.py
│   ├── executor.py
│   └── bundled/
├── agent.py        # Agent factory
├── deps.py         # Deps container
├── protocols.py    # Port interfaces
├── settings.py     # Configuration
└── tools.py        # Tool definitions
```

## Key Principles

1. **Protocols define contracts** - All adapters implement protocols from `protocols.py`
2. **Deps bundles adapters** - One container passed through the request lifecycle
3. **Tools use RunContext** - `ctx.deps` provides access to all adapters
4. **Async everywhere** - All I/O operations are async
5. **Fakes for tests** - In-memory implementations for fast testing

## Source Files

- [protocols.py](../src/openfang/protocols.py) - Port interfaces
- [deps.py](../src/openfang/deps.py) - Deps container
- [agent.py](../src/openfang/agent.py) - Agent factory
- [tools.py](../src/openfang/tools.py) - Tool definitions

---

## OpenClaw Reference

OpenFang is inspired by [OpenClaw](https://github.com/AbanteAI/openclaw) and shares its core design philosophy.

### Shared Architecture

Both projects use **hexagonal architecture** (ports and adapters):
- Protocol interfaces define contracts
- Adapters implement those contracts
- Dependency injection bundles adapters
- Skills as markdown files with YAML frontmatter

### Key Differences

| Aspect | OpenFang | OpenClaw |
|--------|----------|----------|
| **Language** | Python 3.13+ | TypeScript |
| **Framework** | pydantic-ai, FastAPI | Custom agent framework |
| **Gateway** | HTTP REST + SSE | HTTP + WebSocket RPC |
| **Memory** | Simple key-value | Hybrid search (BM25 + vectors) |
| **Size** | ~5K lines | ~75K+ lines |
| **Focus** | Readable, minimal | Feature-complete |

### OpenClaw Directory Structure

```
openclaw/
├── src/
│   ├── agents/           # Agent runtime
│   ├── channels/         # Platform connectors
│   ├── config/           # Configuration
│   ├── gateway/          # HTTP + WebSocket server
│   ├── infra/            # Infrastructure (retry, dedupe, etc.)
│   ├── memory/           # Hybrid memory system
│   ├── routing/          # Agent routing
│   └── telegram/, discord/, slack/
├── skills/               # Bundled skills
└── extensions/           # Plugin channels
```

### Patterns from OpenClaw

See [openclaw-patterns.md](../openclaw-patterns.md) for detailed analysis:

1. **Context Compaction** - Progressive summarization for long conversations
2. **Message Deduplication** - TTL cache to prevent duplicate processing
3. **Conversation Locking** - Serialize concurrent messages per-chat
4. **Message Chunking** - Markdown-aware splitting for platform limits
5. **Agent Routing** - Binding hierarchy for multi-agent setups
6. **Retry with Error Classification** - Smart retry for transient errors
7. **Tool Result Guard** - Ensure consistent tool call/result pairs
8. **Graceful Shutdown** - Signal handlers with timeout
