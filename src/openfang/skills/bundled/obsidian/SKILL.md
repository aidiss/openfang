---
name: obsidian
description: Work with Obsidian vaults as plain Markdown folders.
homepage: https://obsidian.md
metadata:
  { "openfang": { "emoji": "💎" } }
---

# Obsidian

Obsidian vaults are just folders with Markdown files. You can read and edit them directly.

## Vault Structure

```
my-vault/
├── .obsidian/          # Config (don't touch)
├── Notes/
│   ├── daily/
│   │   └── 2024-01-15.md
│   └── projects/
│       └── my-project.md
├── Attachments/        # Images, PDFs
└── Templates/
```

## Find Vault Location

Common locations:

- `~/Documents/Obsidian/`
- `~/Obsidian/`
- iCloud: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/`

## Working with Notes

Notes are plain Markdown with optional YAML frontmatter:

```markdown
---
tags: [project, active]
created: 2024-01-15
---

# My Note

Content with [[wikilinks]] and [regular links](other-note.md).
```

### Search Notes

```bash
# Find notes by name
find ~/Documents/Obsidian -name "*.md" | grep -i "project"

# Search content
grep -r "search term" ~/Documents/Obsidian --include="*.md"
```

### Create Note

```bash
cat > ~/Documents/Obsidian/vault/Notes/new-note.md << 'EOF'
---
created: $(date +%Y-%m-%d)
---

# New Note

Content here.
EOF
```

### Daily Notes

Common pattern: `YYYY-MM-DD.md` in a `daily/` folder:

```bash
TODAY=$(date +%Y-%m-%d)
cat > ~/Documents/Obsidian/vault/daily/$TODAY.md << EOF
# $TODAY

## Tasks
- [ ]

## Notes

EOF
```

## Wikilinks

Obsidian uses `[[wikilinks]]` for internal linking:

- `[[Note Name]]` - link to note
- `[[Note Name|Display Text]]` - custom display text
- `[[Note Name#Heading]]` - link to heading
- `![[Note Name]]` - embed note content

When moving/renaming notes, update wikilinks manually or use Obsidian's built-in rename.

## Tips

- Obsidian auto-refreshes when files change on disk
- Avoid editing `.obsidian/` config directly
- Canvas files (`.canvas`) are JSON
- Attachments are just files; reference with `![[image.png]]`
