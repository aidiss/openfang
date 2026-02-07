# Gateway & Web UI

HTTP server with HTMX-based web interface for interacting with the agent.

## Purpose

The gateway provides:
- **Web UI**: Browser-based chat interface
- **HTTP API**: REST endpoints for programmatic access
- **SSE**: Real-time updates via Server-Sent Events
- **Channel management**: Starts/stops all messaging channels
- **Heartbeat**: Periodic health checks

## Gateway Architecture

```
┌──────────────────────────────────────────────────┐
│                   Gateway                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  │
│  │  FastAPI   │  │  Channels  │  │  Heartbeat │  │
│  │  (HTTP)    │  │  (TG/DC)   │  │  (loop)    │  │
│  └──────┬─────┘  └──────┬─────┘  └──────┬─────┘  │
│         │               │               │        │
│         └───────────────┴───────────────┘        │
│                         │                        │
│                    ┌────┴────┐                   │
│                    │  Deps   │                   │
│                    └─────────┘                   │
└──────────────────────────────────────────────────┘
```

Started with: `python -m openfang gateway`

## HTTP Routes

### Core Routes

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Home page (redirects to chat) |
| GET | `/health` | Health check |
| GET | `/status` | System status |

### Chat Routes

| Method | Path | Description |
|--------|------|-------------|
| GET | `/chat` | Web UI chat page |
| POST | `/chat` | Send message, receive response |

### Conversations

| Method | Path | Description |
|--------|------|-------------|
| GET | `/conversations` | List all conversations |
| GET | `/conversations/{id}` | Get conversation messages |
| DELETE | `/conversations/{id}` | Delete conversation |

### Memory

| Method | Path | Description |
|--------|------|-------------|
| GET | `/memory` | List all memory keys |
| GET | `/memory/{key}` | Get memory value |
| PUT | `/memory/{key}` | Set memory value |
| DELETE | `/memory/{key}` | Delete memory key |

### Cron Jobs

| Method | Path | Description |
|--------|------|-------------|
| GET | `/cron` | List cron jobs |
| POST | `/cron` | Create cron job |
| GET | `/cron/{id}` | Get job details |
| DELETE | `/cron/{id}` | Delete job |
| POST | `/cron/{id}/enable` | Enable job |
| POST | `/cron/{id}/disable` | Disable job |

### Skills

| Method | Path | Description |
|--------|------|-------------|
| GET | `/skills` | List available skills |

### Channels

| Method | Path | Description |
|--------|------|-------------|
| GET | `/channels` | List channels and accounts |
| GET | `/channels/status` | Channel status |

### Events (SSE)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/events` | SSE stream for real-time updates |

### Webhooks

| Method | Path | Description |
|--------|------|-------------|
| POST | `/webhooks/{hook_id}` | Receive external webhooks |

## Web UI

### Technology Stack

- **HTMX**: Dynamic updates without full page reloads
- **Jinja2**: Server-side templating
- **SSE**: Real-time message streaming

### Templates

Location: `src/openfang/gateway/templates/`

```
templates/
├── base.html           # Base layout
├── chat.html           # Main chat interface
├── conversations.html  # Conversation list
├── memory.html         # Memory viewer
├── cron.html           # Cron job manager
├── skills.html         # Skills list
└── partials/
    ├── message.html    # Single message
    └── ...
```

### Chat Flow

1. User types message in form
2. HTMX POSTs to `/chat`
3. Server creates Deps, runs agent
4. Response streamed via SSE or returned directly
5. HTMX swaps response into DOM

## SSE Events

Real-time updates via Server-Sent Events at `/events`:

```javascript
const events = new EventSource('/events');

events.addEventListener('message', (e) => {
  const data = JSON.parse(e.data);
  // Handle: token, done, error
});
```

Event types:
- `token` - Partial response token
- `done` - Response complete
- `error` - Error occurred

## Lifespan Management

The gateway uses FastAPI's lifespan to manage startup/shutdown:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await channels.start_all()
    heartbeat_task = asyncio.create_task(heartbeat_loop())

    yield

    # Shutdown
    heartbeat_task.cancel()
    await channels.stop_all()
```

## Heartbeat System

Periodic health checks that run agent tasks.

### Configuration

```python
heartbeat_enabled: bool = True
heartbeat_interval: int = 1800  # 30 minutes
heartbeat_prompt: str = "Check HEARTBEAT.md if it exists..."
heartbeat_ack_token: str = "HEARTBEAT_OK"
```

### HEARTBEAT.md

If this file exists in the project root, the heartbeat will read it and process any tasks. Expected response: `HEARTBEAT_OK` if nothing needs attention.

## Dependency Injection

Routes use FastAPI's dependency injection to get Deps:

```python
from fastapi import Depends
from .deps import get_deps

@router.post("/chat")
async def chat(
    message: str,
    deps: Deps = Depends(get_deps),
):
    # deps contains all adapters
    response = await agent.run(message, deps=deps)
    return {"response": response.data}
```

## Source Files

- [gateway/app.py](../src/openfang/gateway/app.py) - FastAPI app, lifespan
- [gateway/deps.py](../src/openfang/gateway/deps.py) - Route dependencies
- [gateway/sse.py](../src/openfang/gateway/sse.py) - SSE handler
- [gateway/heartbeat.py](../src/openfang/gateway/heartbeat.py) - Heartbeat loop
- [gateway/routes/](../src/openfang/gateway/routes/) - Route modules
- [gateway/templates/](../src/openfang/gateway/templates/) - HTMX templates

---

## OpenClaw Reference

### Key Files

- `/openclaw/src/gateway/server.impl.ts` - Main gateway initialization
- `/openclaw/src/gateway/server-chat.ts` - Agent event handling
- `/openclaw/src/gateway/server-methods.ts` - RPC method handlers
- `/openclaw/src/gateway/server-channels.ts` - Channel manager
- `/openclaw/src/gateway/server-cron.ts` - Scheduled task execution
- `/openclaw/src/infra/heartbeat-runner.ts` - Heartbeat system

### OpenClaw's Approach

**Unified Gateway**:
- Runs HTTP REST + WebSocket + Web UI in single process
- Serves Control UI (browser-based) via HTMX
- Supports OpenAI Chat Completions API (`POST /v1/chat/completions`)
- Supports OpenResponses API (`POST /v1/responses`)

**Multi-Process Runtime**:
- Starts channels, browser control, heartbeat, cron all in gateway process
- Each subsystem has logging domain (canvas, discovery, channels, cron)
- Graceful shutdown coordination across subsystems

**WebSocket Event Architecture**:
- Real-time events via WebSocket subscriptions
- Broadcast capabilities for multi-client coordination
- Node events (mobile client integration)

**Heartbeat System** (from `openclaw-patterns.md`):
- Per-agent config (interval, prompt, target)
- Smart skipping: empty HEARTBEAT.md, quiet hours, in-flight requests
- Duplicate detection within 24h
- Session tracks `lastHeartbeatText` + `lastHeartbeatSentAt`

**Graceful Shutdown** (from `openclaw-patterns.md`):
- Signal handlers: SIGINT, SIGTERM, SIGQUIT
- Two-level cleanup: session locks + gateway connections
- 5-second timeout then force exit

### Diff: OpenFang vs OpenClaw

| Aspect | OpenFang | OpenClaw |
|--------|----------|----------|
| **Server** | FastAPI (HTTP + SSE) | HTTP + WebSocket + RPC |
| **UI** | HTMX templates | HTMX Control UI |
| **Streaming** | SSE | WebSocket subscriptions |
| **OpenAI compat** | Not implemented | Full `/v1/chat/completions` |
| **Heartbeat** | Simple interval | Smart skipping + dedup |
| **Shutdown** | Lifespan context | Signal handlers + timeout |
| **Multi-node** | Not implemented | Node discovery + presence |

### Future Enhancement Ideas

From OpenClaw patterns:
- Add OpenAI-compatible API endpoints
- Implement WebSocket for real-time events
- Smart heartbeat skipping (quiet hours, dedup)
- Graceful shutdown with timeout
- Health/presence versioning
