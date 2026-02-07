# OpenFang Specifications

This folder contains **specification files** for OpenFang's core features. These specs define the contracts, data models, and interfaces that implementations must follow.

## What is Spec-Driven Development?

Spec-driven development treats **specifications as the source of truth**. Code is generated, validated, and verified against these specs. Rather than documentation being an afterthought, specs drive the implementation.

Benefits:
- **Clarity**: Precise definitions of what each system does
- **Consistency**: All implementations follow the same contracts
- **AI-friendly**: Specs serve as context for AI coding assistants
- **Testable**: Specs define what to test

## Spec Files

| File | Description |
|------|-------------|
| [OVERVIEW.md](OVERVIEW.md) | Architecture and request flow |
| [memory.md](memory.md) | Key-value memory system |
| [skills.md](skills.md) | Skill definitions and eligibility |
| [channels.md](channels.md) | Messaging platform connectors |
| [ui.md](ui.md) | Gateway and Web UI |
| [tools.md](tools.md) | Agent tools and permissions |
| [agents.md](agents.md) | Agent configuration and subagents |
| [protocols.md](protocols.md) | All protocol interfaces |
| [configuration.md](configuration.md) | Settings and environment variables |
| [testing.md](testing.md) | Testing patterns with fakes |

## How to Read These Specs

Each spec file follows a consistent structure:

1. **Purpose** - What this system does
2. **Protocol** - The interface contract (from `protocols.py`)
3. **Data Models** - Pydantic models involved
4. **Current Implementation** - What exists today
5. **Extension Points** - How to add new implementations
6. **Source Files** - Links to actual code

## Relationship to Code

- **Protocols** in `src/openfang/protocols.py` define the port interfaces
- **Capabilities** in `src/openfang/capabilities/` implement those protocols
- **Specs** document the contracts that connect them

When implementing a new adapter (e.g., Redis memory, Slack channel), consult the relevant spec to understand the expected behavior.
