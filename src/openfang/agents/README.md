# Agents

Top-level agent personas defined in YAML configuration files.

Each agent has:
- **Identity** — name, emoji for display
- **Tool policies** — allow/deny lists for tool access
- **Skill allowlists** — which skills are available
- **Subagent permissions** — which subagents can be spawned

Key files:
- `models.py` - `AgentConfig`, `AgentIdentity`, `AgentToolPolicy`
- `registry.py` - Loads and manages agent configs
- `bundled/` - Built-in agent YAML definitions
