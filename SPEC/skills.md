# Skills System

Skills are markdown files with YAML frontmatter that extend the agent's capabilities.

## Purpose

Skills provide:
- **Domain knowledge** for specific tools (Docker, GitHub, Linear)
- **Instructions** the agent should follow when relevant
- **Requirements checking** to ensure dependencies are met

## SKILL.md Format

```markdown
---
name: docker
description: Docker container management
emoji: "🐳"
homepage: https://docker.com
userInvocable: true
disableModelInvocation: false

openfang:
  requires:
    bins: ["docker"]
    env: ["DOCKER_HOST"]
  primaryEnv: DOCKER_HOST
  install:
    - id: docker-desktop
      kind: download
      label: Docker Desktop
      url: https://docker.com/products/docker-desktop
      bins: ["docker"]
  os: ["darwin", "linux"]
  always: false
---

# Docker

You are helping a user work with Docker containers.

## Commands

- `docker ps` - List running containers
- `docker images` - List images
- `docker build -t name .` - Build image

## Best Practices

- Use multi-stage builds
- Don't run as root
- Use .dockerignore
```

## Data Models

### Skill

```python
class Skill(BaseModel):
    name: str
    description: str
    content: str              # Markdown body (instructions)
    base_dir: Path            # Directory containing the skill
    source: str               # "bundled", "workspace", "custom"
    homepage: str | None
    user_invocable: bool      # Can user invoke with /<name>
    disable_model_invocation: bool
    metadata: SkillMetadata
```

### SkillMetadata

```python
class SkillMetadata(BaseModel):
    emoji: str | None
    requires: SkillRequirements
    primary_env: str | None   # Main env var for this skill
    install: list[InstallSpec]
    os: list[str] | None      # ["darwin", "linux"]
    always: bool              # Always include in prompt
```

### SkillRequirements

```python
class SkillRequirements(BaseModel):
    bins: list[str]           # All must be available
    any_bins: list[str]       # At least one must be available
    modules: list[str]        # Python modules that must be importable
    any_modules: list[str]    # At least one module must be importable
    env: list[str]            # Environment variables that must be set
    config: list[str]         # Config paths that must be truthy
```

### InstallSpec

```python
class InstallSpec(BaseModel):
    id: str
    kind: Literal["brew", "apt", "pip", "uv", "node", "download"]
    label: str | None
    formula: str | None       # brew
    package: str | None       # apt, pip, uv, node
    url: str | None           # download
    bins: list[str]
```

## Protocol

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

## Eligibility Checking

A skill is **eligible** when all its requirements are met:

1. **bins**: All binaries exist in PATH (`shutil.which()`)
2. **any_bins**: At least one binary exists
3. **modules**: All Python modules are importable
4. **any_modules**: At least one module is importable
5. **env**: All environment variables are set
6. **os**: Current OS matches (if specified)

## Bundled Skills

Location: `src/openfang/skills/bundled/`

| Skill | Requirements | Description |
|-------|--------------|-------------|
| docker | `bins: [docker]` | Container management |
| github | `bins: [gh]` | GitHub CLI |
| himalaya | `bins: [himalaya]` | Email client |
| youtube | `modules: [yt_dlp]` | Video downloads |
| linear | `env: [LINEAR_API_KEY]` | Issue tracking |
| notion | `env: [NOTION_API_KEY]` | Note-taking |
| obsidian | — | Markdown notes |
| openai-images | `env: [OPENAI_API_KEY]` | Image generation |
| pandas-data | `modules: [pandas]` | Data analysis |
| todoist | `env: [TODOIST_API_KEY]` | Task management |
| trello | `env: [TRELLO_API_KEY]` | Project boards |
| weather | `env: [OPENWEATHER_API_KEY]` | Weather data |
| wikipedia | — | Encyclopedia queries |

## Usage in Agent

Skills are injected into the system prompt via `@agent.instructions`:

```python
@agent.instructions
async def context(ctx: RunContext[Deps]) -> str:
    # ... other context ...
    skills_prompt = ctx.deps.comms.skills.format_for_prompt()
    if skills_prompt:
        lines.append(skills_prompt)
```

## Adding Custom Skills

1. Create `skills/` directory in your project
2. Add `SKILL.md` files following the format above
3. Skills are auto-loaded from workspace directories

## Source Files

- [skills/models.py](../src/openfang/skills/models.py) - Skill, SkillMetadata, SkillRequirements
- [skills/registry.py](../src/openfang/skills/registry.py) - SkillRegistry
- [skills/loader.py](../src/openfang/skills/loader.py) - SKILL.md parsing
- [skills/bundled/](../src/openfang/skills/bundled/) - Built-in skills
- [protocols.py:213-249](../src/openfang/protocols.py) - Skills protocol

---

## OpenClaw Reference

### Key Files

- `/openclaw/src/agents/skills/types.ts` - Core type definitions
- `/openclaw/src/agents/skills/config.ts` - Skill eligibility & config resolution
- `/openclaw/src/agents/skills/frontmatter.ts` - SKILL.md frontmatter parsing
- `/openclaw/src/agents/skills/workspace.ts` - Workspace skill discovery
- `/openclaw/skills/` - Bundled skills (1password, local-places, etc.)

### OpenClaw's Approach

**Markdown-First Skill Definition**:
- Each skill is a `SKILL.md` file with YAML frontmatter
- Metadata lives in `metadata.openclaw` namespace
- Example: `metadata.openclaw.requires.bins: ["op"]`

**Declarative Eligibility**:
- `shouldIncludeSkill()` evaluates against local + remote context
- Remote eligibility checks connected nodes (platform + binary detection)
- Supports "always include" skills

**Install Specifications**:
- Multi-step installation with architecture-specific options
- Kinds: `brew`, `node`, `go`, `uv`, `download`
- Package managers configurable per agent

**Bundled vs Plugin Skills**:
- Core skills in `/openclaw/skills/` (included by default)
- Plugin skills loaded from extensions
- Allowlist system controls exposure

**Skill Invocation Policy**:
- Optional policy controls user vs model invocation
- Prevents model from auto-invoking dangerous skills

### Diff: OpenFang vs OpenClaw

| Aspect | OpenFang | OpenClaw |
|--------|----------|----------|
| **Format** | SKILL.md with YAML | SKILL.md with YAML |
| **Namespace** | `openfang:` | `metadata.openclaw:` |
| **Remote eligibility** | Local only | Local + remote nodes |
| **Install kinds** | brew, apt, pip, uv, node, download | brew, node, go, uv, download |
| **Plugin system** | Not implemented | Extension-based plugins |
| **Invocation policy** | `user_invocable`, `disable_model_invocation` | Dedicated policy object |

### Shared Design

Both OpenFang and OpenClaw share:
- Markdown-first skill definitions
- YAML frontmatter for metadata
- Declarative requirements (bins, env, modules)
- Eligibility checking at runtime
- Install specifications for dependencies
