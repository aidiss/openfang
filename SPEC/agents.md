# Agents & Subagents

Agent configuration, dynamic instructions, and task delegation.

## Purpose

- **Agents**: Top-level personas with configured tools, skills, and permissions
- **Subagents**: Specialized workers for focused task delegation

## Agent Factory

Agents are created via `create_agent()`:

```python
def create_agent(
    model: str | None = None,
    system_prompt: str = "You are a helpful assistant. Be concise.",
) -> Agent[Deps, str]:
    """Create a configured agent with all tools registered."""

    effective_model = model or settings.get_model()
    agent = Agent(
        effective_model,
        deps_type=Deps,
        system_prompt=system_prompt,
        prepare_tools=filter_tools_by_permission,
    )

    # Register tools
    for tool_func in ALL_TOOLS:
        agent.tool(tool_func)

    # Register dynamic instructions
    @agent.instructions
    async def context(ctx: RunContext[Deps]) -> str:
        # Build context from user, project, page, skills, subagents
        ...

    return agent
```

## Dynamic Instructions

The `@agent.instructions` decorator adds runtime context:

```python
@agent.instructions
async def context(ctx: RunContext[Deps]) -> str:
    user = ctx.deps.user
    lines = []

    # User info
    roles = ", ".join(user.roles) if user.roles else "none"
    lines.append(f"User: {user.email} (roles: {roles})")

    # Current project
    cur = await ctx.deps.workspace.projects.current()
    lines.append(f"Project: {cur[0]} at {cur[1]}" if cur else "No project selected.")

    # Current page (for web UI context)
    if ctx.deps.current_page:
        lines.append(f"Viewing: {ctx.deps.current_page}")

    # Access level hint
    if user.is_admin:
        lines.append("Access: admin (all tools including shell)")
    elif user.has_role(Role.DEVELOPER):
        lines.append("Access: developer (file and project tools)")
    else:
        lines.append("Access: standard (web and memory tools)")

    # Eligible skills
    skills_prompt = ctx.deps.comms.skills.format_for_prompt()
    if skills_prompt:
        lines.append(skills_prompt)

    # Available subagents (main agent only)
    if not ctx.deps.is_subagent and ctx.deps.subagents:
        subagents_prompt = ctx.deps.subagents.list_for_prompt()
        if subagents_prompt:
            lines.append(subagents_prompt)

    return "\n".join(lines)
```

## Agent Configuration (YAML)

Location: `src/openfang/agents/bundled/`

```yaml
# main.yaml
identity:
  name: "OpenFang"
  emoji: "🐺"
  description: "Personal AI assistant"

tool_policy:
  allowed: ["*"]
  denied: []

skill_allowlist: ["*"]

subagent_permissions:
  - code_analyzer
  - web_researcher
  - summarizer
```

### AgentConfig Model

```python
class AgentIdentity(BaseModel):
    name: str
    emoji: str
    description: str

class AgentToolPolicy(BaseModel):
    allowed: list[str]  # ["*"] or specific tools
    denied: list[str]

class AgentConfig(BaseModel):
    identity: AgentIdentity
    tool_policy: AgentToolPolicy
    skill_allowlist: list[str]
    subagent_permissions: list[str]
```

## Subagents

Specialized agents for focused task delegation.

### Subagent Spec (YAML)

Location: `src/openfang/subagents/bundled/`

```yaml
# code_analyzer.yaml
id: code_analyzer
name: "Code Analyzer"
description: "Analyzes code structure, finds patterns, identifies issues"
system_prompt: |
  You are a code analysis expert. Focus on:
  - Code structure and patterns
  - Potential bugs and issues
  - Improvement suggestions

tools:
  - file_read
  - file_list
  - file_search

denied_tools: []
max_requests: 10
```

### SubagentSpec Model

```python
class SubagentSpec(BaseModel):
    id: str
    name: str
    description: str
    system_prompt: str
    tools: list[str]       # Allowlisted tools
    denied_tools: list[str]
    max_requests: int      # Max tool calls
```

### Bundled Subagents

| ID | Purpose | Tools |
|----|---------|-------|
| `code_analyzer` | Code structure analysis | file_read, file_list, file_search |
| `web_researcher` | Web research tasks | web_fetch, web_browse, web_screenshot |
| `summarizer` | Content summarization | file_read, memory_get |

### Subagent Execution

```python
class SubagentExecutor:
    async def execute(
        self,
        spec: SubagentSpec,
        task: str,
        deps: Deps,
    ) -> SubagentResult:
        # Create subagent-specific deps
        subagent_deps = replace(
            deps,
            is_subagent=True,
            parent_run_id=...,
        )

        # Create agent with subagent's config
        agent = create_agent(
            system_prompt=spec.system_prompt,
        )

        # Filter to allowed tools
        # Run agent
        # Return result
```

### Subagent Tools

| Tool | Args | Description |
|------|------|-------------|
| `subagent_delegate` | `subagent_id`, `task` | Run task with subagent |
| `subagent_list` | — | List available subagents |

### Subagent Constraints

- **One level deep**: Subagents cannot spawn subagents
- **Tool restrictions**: Only allowed tools available
- **Max requests**: Limited tool calls per execution
- **Synchronous**: Main agent waits for subagent result

## User Model

```python
class User(BaseModel):
    id: int
    email: str
    phone: str | None
    telegram_id: str | None
    roles: set[str]

    @property
    def is_admin(self) -> bool:
        return Role.ADMIN in self.roles

    def has_role(self, role: str) -> bool:
        return role in self.roles
```

### Roles

```python
class Role:
    ADMIN = "admin"
    DEVELOPER = "developer"
```

## Source Files

- [agent.py](../src/openfang/agent.py) - create_agent, @agent.instructions
- [agents/models.py](../src/openfang/agents/models.py) - AgentConfig, AgentIdentity
- [agents/registry.py](../src/openfang/agents/registry.py) - AgentRegistry
- [agents/bundled/](../src/openfang/agents/bundled/) - Agent YAML configs
- [subagents/models.py](../src/openfang/subagents/models.py) - SubagentSpec, SubagentResult
- [subagents/executor.py](../src/openfang/subagents/executor.py) - SubagentExecutor
- [subagents/registry.py](../src/openfang/subagents/registry.py) - SubagentRegistry
- [subagents/tools.py](../src/openfang/subagents/tools.py) - subagent_delegate, subagent_list
- [subagents/bundled/](../src/openfang/subagents/bundled/) - Subagent YAML specs
- [models.py](../src/openfang/models.py) - User, Role

---

## OpenClaw Reference

### Key Files

- `/openclaw/src/agents/agent-scope.ts` - Agent path + workspace resolution
- `/openclaw/src/agents/agent-paths.ts` - Agent directory structure
- `/openclaw/src/agents/auth-profiles.ts` - Multi-account auth management
- `/openclaw/src/agents/defaults.ts` - Default model/provider
- `/openclaw/src/routing/resolve-route.ts` - Agent routing
- `/openclaw/src/agents/compaction.ts` - Context compaction

### OpenClaw's Approach

**Agent Directory Structure**:
```
~/.openclaw/agents/{agentId}/
├── session_memory.db
├── skills/
├── hooks/
├── sessions/
└── workspace/
```

**Agent Routing** (from `openclaw-patterns.md`):
- Binding hierarchy: peer > parent peer > guild > team > account > channel > default
- Pattern matching with wildcards
- Config-driven rules
- Session key includes routing decision

**Multi-Account Auth Profiles**:
- Auth profiles support multiple accounts (OAuth, API keys)
- Profiles can have cooldowns (rate limiting)
- Round-robin selection if multiple available
- Fallback ordering: last-used → stored order → first

**Context Compaction** (from `openclaw-patterns.md`):
- Token-aware chunking using `estimateTokens()`
- Progressive summarization: chunk → summarize → merge
- Fallback chain: full → partial → truncation
- 1.2x safety margin on token estimates

**Session Scope Modes** (from `openclaw-patterns.md`):
- Scope modes: global, per-sender, per-channel-peer
- Session key format: `<agentId>:<scope>:<channel>:<peer>`
- File-based store with atomic writes

### Diff: OpenFang vs OpenClaw

| Aspect | OpenFang | OpenClaw |
|--------|----------|----------|
| **Agent routing** | Single default agent | Binding hierarchy with patterns |
| **Auth profiles** | Not implemented | Multi-account with fallback |
| **Context compaction** | Not implemented | Progressive summarization |
| **Session scopes** | Per-conversation | Global / per-chat / per-user |
| **Directory structure** | In-memory | File-based with SQLite |
| **Hooks** | Not implemented | HOOK.md lifecycle hooks |

### Future Enhancement Ideas

From OpenClaw patterns:
- Add context compaction for long conversations
- Implement agent routing with binding hierarchy
- Support multiple session scope modes
- Multi-account auth profile management
- File-based session persistence
