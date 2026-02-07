# Testing

Testing patterns using fakes over mocks.

## Philosophy

**Fakes over Mocks**: Use in-memory implementations that behave like real adapters, not mock objects with predefined responses.

Benefits:
- Tests verify actual behavior, not mock expectations
- Fakes can be reused across tests
- No brittle mock setup
- Tests run fast (no Docker, no network)

## Test Infrastructure

Location: `tests/conftest.py`

### Fake Adapters

```python
class FakeFiles:
    """In-memory file system."""
    def __init__(self):
        self._files: dict[str, str] = {}
        self.root = Path("/fake")

    async def read(self, path: str) -> str:
        if path not in self._files:
            raise FileNotFoundError(path)
        return self._files[path]

    async def write(self, path: str, content: str) -> None:
        self._files[path] = content

    async def list(self, pattern: str = "**/*") -> list[str]:
        # Glob matching against _files keys
        ...

    async def search(self, pattern: str, file_glob: str = "**/*") -> list[Match]:
        # Regex search in _files values
        ...
```

### Available Fakes

| Fake | Replaces | Behavior |
|------|----------|----------|
| `FakeFiles` | `LocalFiles` | Dict-based file storage |
| `FakeWeb` | `PlaywrightWeb` | Configurable URL responses |
| `FakeShell` | `LocalShell` | Recorded command outputs |
| `FakeProjects` | `LocalProjects` | In-memory project registry |
| `FakeConversations` | `InMemoryConversations` | Already in-memory |
| `FakeCron` | `InMemoryCron` | Already in-memory |

### FakeWeb Example

```python
class FakeWeb:
    def __init__(self):
        self._responses: dict[str, str] = {}

    def set_response(self, url: str, content: str) -> None:
        self._responses[url] = content

    async def fetch(self, url: str) -> str:
        if url in self._responses:
            return self._responses[url]
        raise Exception(f"No fake response for {url}")

    async def browse(self, url: str) -> Page:
        content = await self.fetch(url)
        return Page(url=url, title="Fake Page", text=content)
```

### FakeShell Example

```python
class FakeShell:
    def __init__(self):
        self._commands: dict[str, Result] = {}

    def set_output(self, cmd: str, stdout: str, code: int = 0) -> None:
        self._commands[cmd] = Result(
            ok=(code == 0),
            code=code,
            stdout=stdout,
            stderr="",
        )

    async def exec(self, cmd: str, cwd: Path | None = None) -> Result:
        if cmd in self._commands:
            return self._commands[cmd]
        return Result(ok=False, code=1, stdout="", stderr="Command not found")
```

## Fixtures

```python
@pytest.fixture
def fake_files():
    return FakeFiles()

@pytest.fixture
def fake_web():
    return FakeWeb()

@pytest.fixture
def fake_shell():
    return FakeShell()

@pytest.fixture
def test_user():
    return User(
        id=1,
        email="test@example.com",
        roles={Role.DEVELOPER, Role.ADMIN},
    )

@pytest.fixture
async def test_deps(fake_files, fake_web, fake_shell, test_user):
    """Create Deps with all fakes."""
    deps = Deps(
        user=test_user,
        storage=StorageAdapters(
            files=fake_files,
            memory=InMemoryMemory(),
            conversations=InMemoryConversations(),
        ),
        web_adapters=WebAdapters(web=fake_web),
        workspace=WorkspaceAdapters(
            shell=fake_shell,
            projects=LocalProjects(),
        ),
        scheduling=SchedulingAdapters(cron=InMemoryCron()),
        comms=CommsAdapters(
            channels=ChannelRegistry(),
            skills=SkillRegistry.default(),
        ),
    )
    yield deps
    await deps.close()
```

## Test Examples

### Tool Test

```python
@pytest.mark.asyncio
async def test_file_read(test_deps, fake_files):
    # Arrange
    fake_files._files["test.txt"] = "hello world"

    # Act
    ctx = RunContext(deps=test_deps, ...)
    result = await file_read(ctx, "test.txt")

    # Assert
    assert result == "hello world"
```

### Memory Test

```python
@pytest.mark.asyncio
async def test_memory_roundtrip(test_deps):
    memory = test_deps.storage.memory

    # Set
    await memory.set("key", "value")

    # Get
    result = await memory.get("key")
    assert result == "value"

    # Keys
    keys = await memory.keys()
    assert "key" in keys

    # Delete
    await memory.delete("key")
    assert await memory.get("key") is None
```

### Web Test

```python
@pytest.mark.asyncio
async def test_web_fetch(test_deps, fake_web):
    fake_web.set_response("https://example.com", "Example content")

    ctx = RunContext(deps=test_deps, ...)
    result = await web_fetch(ctx, "https://example.com")

    assert "Example content" in result
```

### Agent Test

```python
@pytest.mark.asyncio
async def test_agent_uses_tool(test_deps, fake_files):
    fake_files._files["data.txt"] = "important data"

    agent = create_agent()
    result = await agent.run(
        "Read the file data.txt",
        deps=test_deps,
    )

    assert "important data" in result.data
```

## Running Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov

# Single file
uv run pytest tests/test_tools.py

# Single test
uv run pytest tests/test_tools.py -k test_memory

# Verbose
uv run pytest -v
```

## Test Organization

```
tests/
├── conftest.py         # Fixtures and fakes
├── test_tools.py       # Tool tests
├── test_memory.py      # Memory tests
├── test_agent.py       # Agent tests
├── test_skills.py      # Skill tests
├── test_channels.py    # Channel tests
└── test_gateway.py     # HTTP route tests
```

## Guidelines

1. **Use fakes, not mocks**: Implement behavior, don't record expectations
2. **Test through public interfaces**: Call tools, not internal methods
3. **Keep tests fast**: No network, no disk, no Docker
4. **One assertion per concept**: Clear failure messages
5. **Arrange-Act-Assert**: Clear test structure

## Source Files

- [tests/conftest.py](../tests/conftest.py) - Fixtures and fakes
- [tests/](../tests/) - Test modules

---

## OpenClaw Reference

### Testing Approach

OpenClaw uses similar "fakes over mocks" philosophy but in TypeScript/Jest.

### Key Differences

| Aspect | OpenFang | OpenClaw |
|--------|----------|----------|
| **Framework** | pytest | Jest/Vitest |
| **Fakes** | Python classes | TypeScript objects |
| **Async** | `pytest.mark.asyncio` | `async/await` native |
| **Fixtures** | `@pytest.fixture` | `beforeEach`/`afterEach` |

### Shared Testing Principles

Both projects emphasize:
- **In-memory adapters** that implement real interfaces
- **No external dependencies** (no Docker, no network)
- **Fast test runs** (~2 seconds)
- **Behavior verification** over mock expectations

### OpenClaw Patterns Relevant to Testing

**Retry with Error Classification** (from `openclaw-patterns.md`):
- Test recoverable vs non-recoverable errors separately
- Verify exponential backoff behavior
- Test fallback chains

**Tool Result Guard**:
- Test that all tool calls have matching results
- Verify synthetic result generation for missing calls

**Message Deduplication**:
- Test TTL expiration
- Test size-bounded cache pruning
- Test composite key generation

### Test Organization Comparison

```
# OpenFang (Python)
tests/
├── conftest.py
├── test_tools.py
└── test_agent.py

# OpenClaw (TypeScript)
src/
├── __tests__/
│   ├── memory.test.ts
│   └── agent.test.ts
└── module/
    └── module.test.ts  # Co-located tests
```
