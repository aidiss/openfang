# Subagents

Specialized task delegation system. The main agent can spawn subagents for focused tasks.

**Bundled subagents:**
- `code_analyzer` - Code review and analysis
- `web_researcher` - Web research tasks
- `summarizer` - Content summarization

**Design:**
- Subagents run synchronously (wait for result)
- Limited tool access per subagent spec
- Results returned inline to parent agent
- One level deep (subagents cannot spawn subagents)

Key files:
- `models.py` - `SubagentSpec`, `SubagentRunRecord`, `SubagentResult`
- `executor.py` - Runs subagent tasks
- `registry.py` - Loads and manages subagent specs
- `tools.py` - `subagent_delegate` tool for main agent
- `bundled/` - Built-in subagent YAML definitions
