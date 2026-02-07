# Protocol Interfaces

All port interfaces that adapters must implement.

## Overview

Protocols define the contracts between the application core and external systems. They use Python's `typing.Protocol` with `@runtime_checkable` for structural subtyping.

Location: `src/openfang/protocols.py`

## Files

File operations scoped to a root directory.

```python
@runtime_checkable
class Files(Protocol):
    root: Path

    async def read(self, path: str) -> str:
        """Read file contents as text."""

    async def write(self, path: str, content: str) -> None:
        """Write content to file, creating parent directories if needed."""

    async def list(self, pattern: str = "**/*") -> list[str]:
        """List files matching a glob pattern."""

    async def search(self, pattern: str, file_glob: str = "**/*") -> list[Match]:
        """Search file contents using regex."""
```

**Implementation**: `LocalFiles` in `capabilities/files.py`

## Web

Web access with stateless and session-based operations.

```python
@runtime_checkable
class Web(Protocol):
    async def fetch(self, url: str) -> str:
        """Fetch URL content as plain text (no JavaScript)."""

    async def browse(self, url: str) -> Page:
        """Browse URL with full JavaScript rendering."""

    async def screenshot(self, url: str) -> bytes:
        """Take a screenshot of a URL."""

    async def session(self) -> WebSession:
        """Create a new stateful browser session."""
```

**Implementation**: `PlaywrightWeb` in `capabilities/web.py`

## WebSession

Stateful browser session for multi-step interactions.

```python
@runtime_checkable
class WebSession(Protocol):
    async def goto(self, url: str) -> Page:
        """Navigate to a URL and return the page content."""

    async def click(self, selector: str) -> Page:
        """Click an element and return the updated page content."""

    async def type(self, selector: str, text: str) -> None:
        """Type text into an input element."""

    async def screenshot(self) -> bytes:
        """Take a screenshot of the current page."""

    async def close(self) -> None:
        """Close the browser session and free resources."""
```

## Memory

Key-value store for persistent data.

```python
@runtime_checkable
class Memory(Protocol):
    async def get(self, key: str) -> str | None:
        """Retrieve a value by key, or None if not found."""

    async def set(self, key: str, value: str) -> None:
        """Store a value under the given key."""

    async def delete(self, key: str) -> None:
        """Delete a key from memory."""

    async def keys(self, prefix: str = "") -> list[str]:
        """List all keys, optionally filtered by prefix."""
```

**Implementation**: `InMemoryMemory` in `capabilities/memory.py`

## Shell

Command execution.

```python
@runtime_checkable
class Shell(Protocol):
    async def exec(self, cmd: str, cwd: Path | None = None) -> Result:
        """Execute a shell command and return the result."""
```

**Result** contains: `ok: bool`, `code: int`, `stdout: str`, `stderr: str`

**Implementation**: `LocalShell` in `capabilities/shell.py`

## Projects

Multi-project workspace management.

```python
@runtime_checkable
class Projects(Protocol):
    async def current(self) -> tuple[str, Path] | None:
        """Get the current project ID and path."""

    async def switch(self, project_id: str) -> Path:
        """Switch to a project and return its root path."""

    async def list(self) -> list[str]:
        """List all registered project IDs."""

    async def register(self, project_id: str, path: Path) -> None:
        """Register a new project."""
```

**Implementation**: `LocalProjects` in `capabilities/projects.py`

## Conversations

Store and retrieve conversation message histories.

```python
@runtime_checkable
class Conversations(Protocol):
    async def get(self, conversation_id: str) -> list[ModelMessage]:
        """Get all messages for a conversation."""

    async def save(self, conversation_id: str, messages: list[ModelMessage]) -> None:
        """Save (replace) all messages for a conversation."""

    async def append(self, conversation_id: str, messages: list[ModelMessage]) -> None:
        """Append messages to a conversation."""

    async def delete(self, conversation_id: str) -> None:
        """Delete a conversation and all its messages."""

    async def list(self, user_id: int | None = None) -> list[str]:
        """List all conversation IDs, optionally filtered by user."""
```

**Implementation**: `InMemoryConversations` in `capabilities/conversations.py`

## Cron

Schedule and manage cron jobs.

```python
@runtime_checkable
class Cron(Protocol):
    async def create(self, schedule: str, task: str, user_id: int | None = None) -> CronJob:
        """Create a new scheduled job."""

    async def get(self, job_id: str) -> CronJob | None:
        """Get a job by ID."""

    async def list(self, user_id: int | None = None) -> list[CronJob]:
        """List all jobs, optionally filtered by user."""

    async def delete(self, job_id: str) -> bool:
        """Delete a job. Returns True if deleted."""

    async def enable(self, job_id: str) -> bool:
        """Enable a job."""

    async def disable(self, job_id: str) -> bool:
        """Disable a job."""
```

**CronJob** contains: `id`, `schedule`, `task`, `enabled`, `created_by`, `created_at`

**Implementation**: `InMemoryCron` in `capabilities/cron.py`

## Skills

Skill registry and discovery.

```python
@runtime_checkable
class Skills(Protocol):
    @property
    def skills(self) -> dict[str, Skill]:
        """All registered skills."""

    def get(self, name: str) -> Skill | None:
        """Get a skill by name."""

    def is_eligible(self, skill: Skill) -> bool:
        """Check if a skill's requirements are met."""

    def eligible_skills(self) -> list[Skill]:
        """List all skills whose requirements are met."""

    def invocable_skills(self) -> list[Skill]:
        """List skills that can be invoked by users."""

    def model_skills(self) -> list[Skill]:
        """List skills available to the model."""

    def format_for_prompt(self, skills: list[Skill] | None = None) -> str:
        """Format skills for inclusion in the system prompt."""

    def load_from_dir(self, path: Path, source: str = "custom") -> None:
        """Load skills from a directory."""
```

**Implementation**: `SkillRegistry` in `skills/registry.py`

## Channel

External messaging platform connector.

```python
@runtime_checkable
class Channel(Protocol):
    id: str  # "telegram", "discord"

    async def start(self, account_id: str) -> None:
        """Start the channel for an account."""

    async def stop(self, account_id: str) -> None:
        """Stop the channel for an account."""

    async def send(self, account_id: str, target: str, text: str) -> bool:
        """Send a message. Returns True on success."""

    async def status(self, account_id: str) -> ChannelStatus:
        """Get the status of an account."""

    def info(self) -> ChannelInfo:
        """Get channel metadata."""

    def set_message_handler(self, handler: MessageHandler | None) -> None:
        """Set callback for inbound messages."""
```

**Implementations**: `TelegramChannel`, `DiscordChannel` in `channels/`

## Channels

Channel registry managing all channel implementations.

```python
@runtime_checkable
class Channels(Protocol):
    def get_channel(self, channel_id: str) -> Channel | None:
    def list_channels(self) -> list[ChannelInfo]:
    async def add_account(self, account: ChannelAccount) -> None:
    async def remove_account(self, channel_id: str, account_id: str) -> None:
    async def list_accounts(self, channel_id: str | None = None) -> list[ChannelAccount]:
    async def start_account(self, channel_id: str, account_id: str) -> None:
    async def stop_account(self, channel_id: str, account_id: str) -> None:
    async def start_all(self) -> None:
    async def stop_all(self) -> None:
    async def status(self) -> list[ChannelStatus]:
    def set_message_handler(self, handler: MessageHandler | None) -> None:
```

**Implementation**: `ChannelRegistry` in `channels/registry.py`

## Type Aliases

```python
# Message handler callback
MessageHandler = Callable[[InboundMessage], Awaitable[None]]

# File search result
@dataclass
class Match:
    path: str
    line: int
    text: str

# Web page result
@dataclass
class Page:
    url: str
    title: str
    text: str

# Shell result
@dataclass
class Result:
    ok: bool
    code: int
    stdout: str
    stderr: str
```

## Source File

- [protocols.py](../src/openfang/protocols.py) - All protocol definitions

---

## OpenClaw Reference

### Architecture Pattern

OpenClaw uses TypeScript interfaces instead of Python protocols, but follows similar hexagonal architecture principles.

### Key Differences

| Aspect | OpenFang | OpenClaw |
|--------|----------|----------|
| **Language** | Python `Protocol` | TypeScript `interface` |
| **Type checking** | `@runtime_checkable` | Compile-time only |
| **Implementation** | Class-based | Object-based |
| **Async** | `async def` | `Promise<T>` |

### OpenClaw Interface Locations

| Domain | OpenClaw Location |
|--------|-------------------|
| Memory | `/openclaw/src/memory/types.ts` |
| Skills | `/openclaw/src/agents/skills/types.ts` |
| Channels | `/openclaw/src/channels/` per-channel |
| Config | `/openclaw/src/config/` |
| Tools | `/openclaw/src/agents/tools/common.ts` |

### Shared Design Principles

Both OpenFang and OpenClaw share:
- **Port interfaces** define contracts (protocols/interfaces)
- **Adapters** implement those contracts
- **Dependency injection** via container objects
- **Async-first** design for all I/O operations
- **Pluggable backends** for storage, channels, etc.

### Notable OpenClaw Patterns

**Diagnostic Events** (from `openclaw-patterns.md`):
- Typed event payloads with `EventType` enum
- In-memory listener registry
- Structured fields: type, timestamp, sequence, payload
- Usage tracking: tokens, cache hits, duration, cost

**Retry with Error Classification** (from `openclaw-patterns.md`):
- Classify errors: `isRecoverableTelegramNetworkError()`
- Exponential backoff for recoverable errors
- Compaction retry: if context overflow, reset and retry
