# Tools System

Agent tools provide capabilities for file operations, web access, memory, and more.

## Purpose

Tools are functions the agent can call to interact with the world. Each tool:
- Has a clear, documented purpose
- Uses `@tool_errors` decorator for error handling
- Accesses adapters via `RunContext[Deps]`
- May be restricted by user role

## Tool Categories

### Files

| Tool | Args | Permission | Description |
|------|------|------------|-------------|
| `file_read` | `path` | developer | Read file contents |
| `file_write` | `path`, `content` | developer | Write to file |
| `file_list` | `glob` | developer | List files matching pattern |
| `file_search` | `pattern`, `glob` | developer | Search with regex |

### Web (Stateless)

| Tool | Args | Permission | Description |
|------|------|------------|-------------|
| `web_fetch` | `url` | all | Fetch URL as text (no JS) |
| `web_browse` | `url` | all | Browse with JS rendering |
| `web_screenshot` | `url` | all | Screenshot a URL |

### Web (Sessions)

| Tool | Args | Permission | Description |
|------|------|------------|-------------|
| `web_session_start` | — | all | Start browser session |
| `web_session_goto` | `session_id`, `url` | all | Navigate session |
| `web_session_click` | `session_id`, `selector` | all | Click element |
| `web_session_type` | `session_id`, `selector`, `text` | all | Type into input |
| `web_session_end` | `session_id` | all | Close session |

### Memory

| Tool | Args | Permission | Description |
|------|------|------------|-------------|
| `memory_set` | `key`, `value` | all | Store value |
| `memory_get` | `key` | all | Retrieve value |
| `memory_delete` | `key` | all | Delete key |
| `memory_list` | `prefix` | all | List keys |

### Shell

| Tool | Args | Permission | Description |
|------|------|------------|-------------|
| `shell_exec` | `cmd`, `cwd` | **admin** | Execute shell command |

### Projects

| Tool | Args | Permission | Description |
|------|------|------------|-------------|
| `project_current` | — | developer | Get current project |
| `project_list` | — | developer | List all projects |
| `project_switch` | `project_id` | developer | Switch project |
| `project_register` | `project_id`, `path` | admin | Register new project |

### Cron

| Tool | Args | Permission | Description |
|------|------|------------|-------------|
| `cron_create` | `schedule`, `task` | developer | Create job |
| `cron_get` | `job_id` | developer | Get job details |
| `cron_list` | — | developer | List jobs |
| `cron_enable` | `job_id` | developer | Enable job |
| `cron_disable` | `job_id` | developer | Disable job |
| `cron_delete` | `job_id` | admin | Delete job |

### Channels

| Tool | Args | Permission | Description |
|------|------|------------|-------------|
| `telegram_send` | `chat_id`, `message` | all | Send Telegram message |
| `discord_send` | `channel_id`, `message` | all | Send Discord message |

### Subagents

| Tool | Args | Permission | Description |
|------|------|------------|-------------|
| `subagent_delegate` | `subagent_id`, `task` | developer | Delegate to subagent |
| `subagent_list` | — | developer | List available subagents |

## Permission Model

```python
TOOL_PERMISSIONS: dict[str, set[str] | None] = {
    # None = all users
    "web_fetch": None,
    "memory_set": None,

    # Developer or Admin
    "file_read": {Role.DEVELOPER, Role.ADMIN},
    "project_switch": {Role.DEVELOPER, Role.ADMIN},

    # Admin only
    "shell_exec": {Role.ADMIN},
    "cron_delete": {Role.ADMIN},
}
```

Filtering applied via `prepare_tools`:

```python
async def filter_tools_by_permission(
    ctx: RunContext[Deps],
    tool_defs: list[ToolDefinition]
) -> list[ToolDefinition]:
    user = ctx.deps.user
    allowed = []
    for tool_def in tool_defs:
        required_roles = TOOL_PERMISSIONS.get(tool_def.name)
        if required_roles is None or user.roles & required_roles:
            allowed.append(tool_def)
    return allowed
```

## Error Handling

The `@tool_errors` decorator catches exceptions and returns error strings:

```python
def tool_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except FileNotFoundError as e:
            return f"Error: File not found: {e.filename}"
        except PermissionError as e:
            return f"Error: Permission denied: {e.filename}"
        except Exception as e:
            return f"Error: {e}"
    return wrapper
```

## Tool Structure

Each tool follows this pattern:

```python
@tool_errors
async def tool_name(ctx: RunContext[Deps], arg1: str, arg2: int = 0) -> str:
    """Tool description.

    Args:
        arg1: Description of arg1.
        arg2: Description of arg2.
    """
    # Access adapters via ctx.deps
    result = await ctx.deps.storage.files.read(arg1)
    return result
```

## Tool Registration

All tools are registered in `ALL_TOOLS` and added to the agent:

```python
ALL_TOOLS = [
    file_read,
    file_write,
    # ... all tools
    *SUBAGENT_TOOLS,  # subagent_delegate, subagent_list
]

# In create_agent()
for tool_func in ALL_TOOLS:
    agent.tool(tool_func)
```

## Output Limits

Tools truncate large outputs to avoid context overflow:

```python
MAX_FETCH_CHARS = 50000
MAX_BROWSE_CHARS = 30000
MAX_SESSION_CHARS = 20000
MAX_SHELL_OUTPUT = 10000
MAX_LS_RESULTS = 500
MAX_GREP_RESULTS = 100
```

## Adding New Tools

1. Add function in `tools.py`:

```python
@tool_errors
async def my_tool(ctx: RunContext[Deps], arg: str) -> str:
    """Do something useful."""
    # Implementation
    return "result"
```

2. Add to `ALL_TOOLS` list
3. Add permission entry in `agent.py`:

```python
TOOL_PERMISSIONS["my_tool"] = {Role.DEVELOPER, Role.ADMIN}
```

## Source Files

- [tools.py](../src/openfang/tools.py) - All tool definitions
- [agent.py](../src/openfang/agent.py) - TOOL_PERMISSIONS, filter_tools_by_permission
- [constants.py](../src/openfang/constants.py) - Output limits

---

## OpenClaw Reference

### Key Files

- `/openclaw/src/agents/tools/common.ts` - Tool utilities and parameter readers
- `/openclaw/src/agents/openclaw-tools.ts` - Tool factory function
- `/openclaw/src/agents/tools/` - Individual tool implementations
- `/openclaw/src/infra/exec-approvals.ts` - Approval flow
- `/openclaw/src/agents/session-tool-result-guard.ts` - Tool result tracking

### OpenClaw's Approach

**Dependency Injection Pattern**:
- `createOpenClawTools(options)` returns tool array
- Options include session context, channel info, sandbox settings
- Tools created on-demand with full context

**Action Gates**:
- `createActionGate<T>()` utility for channel-specific feature toggling
- Each platform tool can enable/disable actions
- Default behavior configurable, explicit override possible

**Parameter Readers**:
- `readStringParam()`, `readNumberParam()` helpers
- Consistent error handling with labels
- Supports required/optional, trim

**Tool Schema Design**:
- Uses TypeBox for schema definition
- Guardrails: avoid `Type.Union`, no `anyOf`/`oneOf`/`allOf`
- Prefer `stringEnum` for discrete options
- Top-level schema always `type: "object"`

**Approval Flow** (from `openclaw-patterns.md`):
- Three-tier security: deny / allowlist / full
- Per-agent allowlist with glob patterns
- Ask modes: off / on-miss / always

**Tool Result Guard** (from `openclaw-patterns.md`):
- Track pending tool call IDs
- Synthesize missing results: `makeMissingToolResult()`
- Ensures consistent transcripts

### Diff: OpenFang vs OpenClaw

| Aspect | OpenFang | OpenClaw |
|--------|----------|----------|
| **Schema** | Python type hints | TypeBox schemas |
| **Permissions** | Role-based dict | Allowlist with glob patterns |
| **Approval flow** | Not implemented | Three-tier (deny/allowlist/full) |
| **Action gates** | Not implemented | Per-channel feature toggles |
| **Result guard** | Not implemented | Synthetic results for missing |
| **Parameter helpers** | Basic | Rich readers with labels |

### Future Enhancement Ideas

From OpenClaw patterns:
- Add approval flow for dangerous operations
- Implement action gates for channel-specific tools
- Tool result guard for consistent transcripts
- Glob-pattern allowlists for fine-grained control
