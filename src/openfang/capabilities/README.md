# Capabilities

Core adapter implementations for the agent's abilities.

| Adapter | Protocol | Purpose |
|---------|----------|---------|
| `LocalFiles` | `Files` | Read/write/search files |
| `PlaywrightWeb` | `Web` | Browse pages, take screenshots |
| `InMemoryMemory` | `Memory` | Key-value storage |
| `LocalShell` | `Shell` | Execute commands |
| `LocalProjects` | `Projects` | Multi-project workspace |
| `InMemorySessions` | `Sessions` | Message history |
| `InMemoryCron` | `Cron` | Scheduled jobs |

All adapters implement protocols defined in `../protocols.py`.
