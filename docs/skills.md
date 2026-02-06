# Skills

Skills extend agent capabilities through Markdown files. No code required — just prompt engineering.

## What Are Skills?

Skills are `SKILL.md` files with:

1. **YAML frontmatter** — Metadata, requirements, install instructions
2. **Markdown body** — Instructions injected into the agent's system prompt

When a skill is eligible (requirements met), its instructions are included in the agent's context.

## Bundled Skills

OpenFang ships with these skills:

| Skill | Description | Requirements |
|-------|-------------|--------------|
| :material-github: **GitHub** | PR checks, issues, API queries | `gh` CLI installed |
| :material-file-document: **Notion** | Page management | `NOTION_TOKEN` env var |
| :material-weather-sunny: **Weather** | Weather lookups | None |

## Using Skills

Skills are automatically loaded and checked for eligibility. View available skills in the gateway UI under **Skills**.

### Check Skill Status

```bash
# Via gateway UI
open http://localhost:18789  # Go to Skills tab

# Or via API
curl http://localhost:18789/skills
```

### Install Missing Requirements

If a skill shows as "unavailable", install its requirements:

```bash
# GitHub skill needs gh CLI
brew install gh  # macOS
apt install gh   # Ubuntu

# Notion skill needs token
export NOTION_TOKEN=secret_xxx
```

## Creating Skills

### Basic Structure

Create `SKILL.md` in `src/openfang/skills/bundled/yourskill/`:

```markdown
---
name: myskill
description: "One-line description of what it does"
metadata:
  openfang:
    emoji: "🔧"
    requires:
      bins: ["mytool"]        # Required CLI tools
      env: ["MY_API_KEY"]     # Required env vars
---

# My Skill

Instructions for the agent go here. Be specific and give examples.

## Example Commands

\`\`\`bash
mytool do-something --flag
\`\`\`

## Important Notes

- Always use `--verbose` for debugging
- Never run `mytool delete` without confirmation
```

### Frontmatter Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Unique skill identifier |
| `description` | string | Short description (shown in UI) |
| `metadata.openfang.emoji` | string | Icon for the skill |
| `metadata.openfang.requires.bins` | list | Required CLI tools |
| `metadata.openfang.requires.env` | list | Required environment variables |
| `metadata.openfang.install` | list | Installation instructions |

### Installation Instructions

Help users install requirements:

```yaml
metadata:
  openfang:
    requires:
      bins: ["gh"]
    install:
      - id: brew
        kind: brew
        formula: gh
        bins: ["gh"]
        label: "Install GitHub CLI (brew)"
      - id: apt
        kind: apt
        package: gh
        bins: ["gh"]
        label: "Install GitHub CLI (apt)"
```

### Writing Good Instructions

1. **Be specific** — Don't say "use the CLI", say "run `gh pr list`"
2. **Give examples** — Show actual commands with expected output
3. **Explain flags** — Document important options
4. **Add warnings** — Note destructive or slow operations

## Example: Weather Skill

```markdown
---
name: weather
description: "Get weather forecasts using wttr.in"
metadata:
  openfang:
    emoji: "🌤️"
---

# Weather Skill

Use wttr.in for weather lookups. It's a free service, no API key needed.

## Get Current Weather

\`\`\`bash
curl -s "wttr.in/London?format=3"
\`\`\`

Output: `London: ⛅️ +15°C`

## Detailed Forecast

\`\`\`bash
curl -s "wttr.in/London"
\`\`\`

## Specific Format

\`\`\`bash
curl -s "wttr.in/London?format=%l:+%c+%t+%w"
\`\`\`

Format codes:
- `%l` — Location
- `%c` — Weather condition emoji
- `%t` — Temperature
- `%w` — Wind
```

## Skill Loading

Skills are loaded at startup from:

1. `src/openfang/skills/bundled/` — Built-in skills
2. Future: workspace skills, managed skills

The `SkillRegistry` checks eligibility:

```python
registry = SkillRegistry.default()

# Get all eligible skills
eligible = registry.get_eligible_skills()

# Check specific skill
if registry.is_eligible("github"):
    print("GitHub skill available")
```

## See Also

- [Architecture](architecture.md) — How skills integrate with the agent
- [GitHub Skill Source](https://github.com/aidiss/openfang/blob/main/src/openfang/skills/bundled/github/SKILL.md)
