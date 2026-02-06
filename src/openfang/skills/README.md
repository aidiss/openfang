# Skills

Agent capabilities defined as SKILL.md files with YAML frontmatter.

Skills are prompt engineering, not code plugins - they provide instructions and requirements that get injected into the agent's system prompt.

Key files:
- `loader.py` - Parses SKILL.md files (frontmatter + markdown body)
- `registry.py` - Manages skills, checks eligibility (bins, env vars)
- `models.py` - `Skill`, `SkillMetadata`, `SkillRequirements`
- `bundled/` - Built-in skills (GitHub, Notion, Weather)
