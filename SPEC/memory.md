# Memory System

Persistent key-value storage for agent state, user preferences, and long-term memory.

## Purpose

The Memory system provides a simple key-value store that persists across conversations. Use cases:
- User preferences ("theme: dark")
- Context that should survive restarts ("last_project: foo")
- Structured data the agent needs to recall ("user_api_keys")

## Protocol

```python
@runtime_checkable
class Memory(Protocol):
    """Key-value store."""

    async def get(self, key: str) -> str | None:
        """Retrieve a value by key, or None if not found."""
        ...

    async def set(self, key: str, value: str) -> None:
        """Store a value under the given key."""
        ...

    async def delete(self, key: str) -> None:
        """Delete a key from memory."""
        ...

    async def keys(self, prefix: str = "") -> list[str]:
        """List all keys, optionally filtered by prefix."""
        ...
```

## Data Model

- **Keys**: Strings, recommended format: `namespace:identifier` (e.g., `user:prefs`, `project:myapp:config`)
- **Values**: Strings (serialize JSON/YAML if needed)
- **Prefix queries**: `keys("user:")` returns all keys starting with "user:"

## Tools

| Tool | Args | Description |
|------|------|-------------|
| `memory_set` | `key`, `value` | Store a value |
| `memory_get` | `key` | Retrieve a value |
| `memory_delete` | `key` | Delete a key |
| `memory_list` | `prefix` (optional) | List keys |

All memory tools are available to **all users** (no role restriction).

## Current Implementation

### InMemoryMemory

Location: `src/openfang/capabilities/memory.py`

```python
class InMemoryMemory:
    """In-memory dict-based memory (non-persistent)."""

    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        return self._data.get(key)

    async def set(self, key: str, value: str) -> None:
        self._data[key] = value

    async def delete(self, key: str) -> None:
        self._data.pop(key, None)

    async def keys(self, prefix: str = "") -> list[str]:
        if not prefix:
            return list(self._data.keys())
        return [k for k in self._data.keys() if k.startswith(prefix)]
```

**Limitations**:
- Data lost on restart (in-memory only)
- No TTL/expiration
- No transactions

## Extension Points

### Redis Implementation

```python
class RedisMemory:
    def __init__(self, client: redis.Redis):
        self._client = client

    async def get(self, key: str) -> str | None:
        return await self._client.get(key)

    async def set(self, key: str, value: str) -> None:
        await self._client.set(key, value)

    async def delete(self, key: str) -> None:
        await self._client.delete(key)

    async def keys(self, prefix: str = "") -> list[str]:
        pattern = f"{prefix}*" if prefix else "*"
        return [k async for k in self._client.scan_iter(pattern)]
```

### PostgreSQL Implementation

```python
class PostgresMemory:
    """Use a simple key/value table."""
    # CREATE TABLE memory (key TEXT PRIMARY KEY, value TEXT, updated_at TIMESTAMP)
```

## Usage in Deps

Memory is accessed via `deps.storage.memory`:

```python
# In a tool
async def memory_set(ctx: RunContext[Deps], key: str, value: str) -> str:
    await ctx.deps.storage.memory.set(key, value)
    return f"Stored: {key}"
```

## Source Files

- [protocols.py:108-126](../src/openfang/protocols.py) - Memory protocol
- [capabilities/memory.py](../src/openfang/capabilities/memory.py) - InMemoryMemory
- [tools.py:238-281](../src/openfang/tools.py) - Memory tools
- [deps.py](../src/openfang/deps.py) - StorageAdapters.memory

---

## OpenClaw Reference

### Key Files

- `/openclaw/src/memory/manager.ts` - Core memory index manager
- `/openclaw/src/memory/hybrid.ts` - Hybrid search (BM25 + vector)
- `/openclaw/src/memory/embeddings.ts` - Embedding provider abstraction
- `/openclaw/src/agents/tools/memory-tool.ts` - Agent integration

### OpenClaw's Approach

**Hybrid Search Architecture**:
- Combines BM25 full-text search with vector search
- BM25 provides keyword accuracy, vectors handle semantic similarity
- Results merged with intelligent scoring strategy

**Pluggable Embedding Providers**:
- Supports OpenAI, Gemini, local (node-llama), or QMD (quantum)
- Automatic fallback when primary fails
- Batch API support for cost efficiency

**Memory File Organization**:
- Root-level `MEMORY.md` for high-level facts
- `memory/` subdirectory for organized chunks
- Automatic chunking with configurable overlap
- Session transcripts indexed separately

**Session-Aware Search**:
- Filter search to specific session key
- Citation support with source tracking

### Diff: OpenFang vs OpenClaw

| Aspect | OpenFang | OpenClaw |
|--------|----------|----------|
| **Storage** | Simple key-value | Hybrid search (BM25 + vectors) |
| **Search** | Prefix queries only | Semantic + keyword search |
| **Persistence** | In-memory (pluggable) | SQLite with sqlite-vec |
| **Embeddings** | None | Multi-provider (OpenAI, Gemini, local) |
| **Complexity** | ~50 lines | ~75k lines |
| **Use case** | Simple preferences | Full semantic memory |

### Future Enhancement Ideas

From OpenClaw patterns:
- Add hybrid search with embeddings
- Support `MEMORY.md` file parsing
- Session-aware memory scoping
- Citation tracking for responses
