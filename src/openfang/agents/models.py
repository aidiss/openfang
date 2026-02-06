"""Top-level agent models - config, identity, and policies."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AgentIdentity(BaseModel):
    """Agent identity for display purposes."""

    name: str = "Assistant"
    """Display name for the agent."""

    emoji: str = "🤖"
    """Single emoji representing the agent."""


class AgentToolPolicy(BaseModel):
    """Tool access policy for an agent."""

    allow: list[str] | None = None
    """Allowlist of tool names. If None, all tools allowed (minus deny list)."""

    deny: list[str] = Field(default_factory=list)
    """Denylist of tool names. Applied after allowlist."""


class AgentConfig(BaseModel):
    """Configuration for a top-level agent."""

    id: str
    """Unique identifier, e.g. 'main', 'coding'."""

    name: str
    """Human-readable display name."""

    default: bool = False
    """Whether this is the default agent for the system."""

    model: str | None = None
    """Model override. If None, uses system default."""

    system_prompt: str | None = None
    """Custom system prompt. If None, uses default."""

    identity: AgentIdentity = Field(default_factory=AgentIdentity)
    """Agent identity (name, emoji)."""

    tools: AgentToolPolicy = Field(default_factory=AgentToolPolicy)
    """Tool access policy."""

    skills: list[str] | None = None
    """Skill allowlist. If None, all skills available."""

    subagent_allow: list[str] = Field(default_factory=lambda: ["*"])
    """Which subagents this agent can spawn. ['*'] means all."""

    def can_use_tool(self, tool_name: str) -> bool:
        """Check if this agent can use a specific tool."""
        # Check deny list first
        if tool_name in self.tools.deny:
            return False

        # If allow list is set, must be in it
        if self.tools.allow is not None:
            return tool_name in self.tools.allow

        # No allow list means all tools allowed (minus deny)
        return True

    def can_spawn_subagent(self, subagent_id: str) -> bool:
        """Check if this agent can spawn a specific subagent."""
        if "*" in self.subagent_allow:
            return True
        return subagent_id in self.subagent_allow
