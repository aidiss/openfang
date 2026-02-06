# OpenFang vs OpenClaw

This document compares OpenFang's implementation to OpenClaw (the reference implementation), explaining our design choices.

---

## Fundamental Differences

| Aspect | OpenClaw | OpenFang | Why Different |
|--------|----------|----------|---------------|
| **Language** | TypeScript | Python 3.13+ | Python ecosystem, Pydantic, easier AI/ML integration |
| **Agent Framework** | Custom agent loop | pydantic-ai | Battle-tested, maintained, typed |
| **Validation** | Zod schemas | Pydantic models | Native Python, same philosophy |
| **Architecture** | Modular TypeScript | Hexagonal (ports & adapters) | Clean separation, testability |
| **Config Format** | JSON | YAML | More human-readable |
| **Testing** | Mocks | Fakes over mocks | More realistic, easier to reason about |
| **Package Manager** | npm/pnpm | uv | Fast, modern Python tooling |
| **UI** | Custom web UI (TypeScript) | Gateway-integrated (HTMX + Alpine.js) | Simpler stack, no build step |

---

## UI Approach

| Aspect | OpenClaw | OpenFang | Why Different |
|--------|----------|----------|---------------|
| **Primary UI** | Custom TypeScript web app | Gateway-integrated dashboard | No separate frontend repo |
| **Framework** | TypeScript + custom components | HTMX + Alpine.js + Tailwind | No build step, hypermedia-driven |
| **State Management** | Custom TypeScript | Alpine.js reactive | Simpler, declarative |
| **Real-time** | WebSocket | SSE (Server-Sent Events) | Standard HTTP, easier debugging |
| **Styling** | Custom CSS | Tailwind CDN | No build, utility-first |

### OpenClaw Web UI
- Separate TypeScript frontend
- Custom component library
- WebSocket for real-time updates
- Agent selector with avatars
- Tabbed interface (Overview, Files, Tools, Skills, Channels, Cron)
- Tool permission toggles
- Model selection dropdowns

### OpenFang Web UI
Built into gateway at `/` - no separate frontend:

- **Dashboard Views:**
  - Chat (real-time via SSE)
  - Overview (stats cards: uptime, skills, channels, memory, cron)
  - Channels (manage Telegram/Discord accounts)
  - Conversations (create, switch, delete sessions)
  - Skills (view available skills)
  - Memory (key-value management)
  - Cron (scheduled tasks)

- **Features:**
  - Dark/light mode toggle
  - Health badge (auto-updates every 10s)
  - Keyboard shortcuts (Ctrl+K focus, Ctrl+N new session)
  - Markdown + syntax highlighting
  - Python-themed branding (🐍)

- **Tech Stack:**
  - HTMX for dynamic updates without page refresh
  - Alpine.js for reactive state
  - Tailwind CSS (CDN)
  - Jinja2 templates
  - No build step, no node_modules

### CLI Commands
```bash
openfang gateway    # Start web UI + API (localhost:18789)
openfang chat       # Interactive terminal chat
openfang run "..."  # Single-shot prompt
openfang health     # Check gateway health
openfang status     # Full gateway status
openfang skills     # List available skills
openfang config     # Show configuration
```

**Why HTMX + Alpine.js?**
1. **No build step**: Templates served directly, CDN for JS/CSS
2. **Hypermedia-driven**: Server returns HTML, not JSON
3. **Simpler debugging**: Standard HTTP requests, view source works
4. **Less code**: No frontend framework boilerplate
5. **Fast iteration**: Edit template, refresh browser

---

## Why Python?

1. **AI/ML Ecosystem**: Python dominates AI tooling (LangChain, LlamaIndex, HuggingFace)
2. **Pydantic**: Native validation, serialization, and settings management
3. **Type Hints**: Modern Python has excellent typing support
4. **Async**: First-class async/await, similar to TypeScript
5. **Simpler Deployment**: Single runtime, no transpilation

---

## Why pydantic-ai?

Instead of building a custom agent loop like OpenClaw, we use pydantic-ai:

| OpenClaw (Custom) | OpenFang (pydantic-ai) |
|-------------------|------------------------|
| Custom tool registration | `@agent.tool` decorator |
| Manual message history | Built-in conversation management |
| Custom streaming | Native streaming support |
| Manual retries/errors | Built-in retry logic |
| Custom usage tracking | `result.usage()` API |

```python
# OpenFang - clean, declarative
agent = Agent("openai:gpt-4o", deps_type=Deps)

@agent.tool
async def file_read(ctx: RunContext[Deps], path: str) -> str:
    return await ctx.deps.storage.files.read(path)

result = await agent.run("Read the config file", deps=deps)
```

---

## Architecture

### OpenClaw
```
src/
├── agents/tools/          # Tool implementations
├── auto-reply/            # Message handling
├── config/                # Zod schemas
├── gateway/               # HTTP/WebSocket server
└── process/               # Agent execution
```

### OpenFang (Hexagonal)
```
src/openfang/
├── protocols.py           # Port interfaces (what)
├── capabilities/          # Adapters (how)
├── deps.py                # Dependency injection
├── agent.py               # Agent factory
├── agents/                # Top-level agent configs
├── subagents/             # Task delegation
├── channels/              # Messaging platforms
├── skills/                # Capability extensions
└── routing/               # Message routing
```

```
┌─────────────────────────────────────────────────────────────┐
│                        Application                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   pydantic-ai Agent                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                                │
│                       Deps Container                        │
│                            │                                │
│  ┌─────────┬─────────┬─────────┬─────────┬─────────────┐   │
│  │ Storage │   Web   │Workspace│Scheduling│    Comms   │   │
│  └────┬────┴────┬────┴────┬────┴────┬────┴──────┬─────┘   │
└───────┼─────────┼─────────┼─────────┼───────────┼─────────┘
   ┌────▼────┐┌───▼───┐┌────▼────┐┌───▼───┐┌─────▼─────┐
   │  Files  ││  Web  ││  Shell  ││  Cron ││  Channels │
   │ Memory  ││Browser││Projects ││       ││  Skills   │
   └─────────┘└───────┘└─────────┘└───────┘└───────────┘
```

---

## Feature Comparison

### Agents (Top-Level Personas)

| Aspect | OpenClaw | OpenFang | Why Different |
|--------|----------|----------|---------------|
| **Config location** | `~/.openclaw/openclaw.json` | `agents/bundled/*.yaml` | YAML more readable |
| **Identity** | name, emoji, avatar, theme | name, emoji | Start minimal |
| **Tool filtering** | Profiles (minimal/coding/full) | Allow/deny lists | More explicit |
| **Model selection** | Primary + fallbacks | Single model | Simpler, add fallbacks later |

### Subagents (Task Delegation)

| Aspect | OpenClaw | OpenFang | Why Different |
|--------|----------|----------|---------------|
| **Tool name** | `sessions_spawn` | `subagent_delegate` | Clearer intent |
| **Execution** | Async (fire & announce) | Sync (wait for result) | Simpler mental model first |
| **Result delivery** | Announced to channel | Returned inline | Easier to use |
| **Nesting** | One level deep | One level deep | Same - prevents recursion |

### Skills

| Aspect | OpenClaw | OpenFang | Why Different |
|--------|----------|----------|---------------|
| **Format** | Markdown + YAML frontmatter | Same | Works well |
| **Loading** | From directory | From directory | Same |
| **Injection** | System prompt | `@agent.instructions` | pydantic-ai pattern |

### Channels

| Aspect | OpenClaw | OpenFang | Why Different |
|--------|----------|----------|---------------|
| **Interface** | TypeScript interface | Python Protocol | Native typing |
| **Platforms** | Telegram, Discord, etc. | Same | Same requirements |
| **Routing** | Config bindings | Session key resolver | Simpler |

### Memory

| Aspect | OpenClaw | OpenFang | Why Different |
|--------|----------|----------|---------------|
| **Storage** | File-based + semantic search | Key-value (in-memory) | Start simple |
| **Scope** | Per-agent workspace | Per-conversation | Simpler isolation |
| **Future** | - | Vector store adapter | Extensible via protocols |

### Heartbeat

| Aspect | OpenClaw | OpenFang | Why Different |
|--------|----------|----------|---------------|
| **Status** | Implemented | Not yet | Lower priority |
| **Future** | - | Via cron + channel send | Use existing primitives |

---

## Testing Philosophy

| OpenClaw | OpenFang |
|----------|----------|
| Mocks for external services | Fakes (in-memory implementations) |
| Test doubles | Real implementations that work in memory |

```python
# OpenFang testing with fakes
@dataclass
class FakeFiles:
    files: dict[str, str] = field(default_factory=dict)

    async def read(self, path: str) -> str:
        if path not in self.files:
            raise FileNotFoundError(path)
        return self.files[path]

    async def write(self, path: str, content: str) -> None:
        self.files[path] = content

# Tests use real logic, just in memory
deps.storage.files = FakeFiles(files={"config.yaml": "key: value"})
result = await file_read(ctx, "config.yaml")
assert result == "key: value"
```

---

## Summary

OpenFang takes inspiration from OpenClaw but makes deliberate choices:

1. **Python over TypeScript**: Better AI ecosystem, Pydantic validation
2. **pydantic-ai over custom**: Leverage maintained framework
3. **Hexagonal architecture**: Clean port/adapter separation
4. **YAML over JSON**: More human-readable configs
5. **Fakes over mocks**: More realistic testing
6. **Sync-first subagents**: Simpler mental model, add async later
7. **Gradual complexity**: Start minimal, add features as needed
