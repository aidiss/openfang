"""Agent registry - loads and manages top-level agent configs."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from .models import AgentConfig

if TYPE_CHECKING:
    from collections.abc import Iterable

    from pydantic_ai import Agent

    from ..deps import Deps

# Bundled configs directory (relative to this file)
BUNDLED_DIR = Path(__file__).parent / "bundled"


class AgentRegistry:
    """Registry for top-level agent configurations."""

    def __init__(self) -> None:
        self._configs: dict[str, AgentConfig] = {}
        self._default_id: str | None = None

    def register(self, config: AgentConfig) -> None:
        """Register an agent config."""
        self._configs[config.id] = config
        if config.default:
            self._default_id = config.id

    def get(self, agent_id: str) -> AgentConfig | None:
        """Get an agent config by ID."""
        return self._configs.get(agent_id)

    def get_default(self) -> AgentConfig | None:
        """Get the default agent config."""
        if self._default_id:
            return self._configs.get(self._default_id)
        # Fall back to first config if no explicit default
        if self._configs:
            return next(iter(self._configs.values()))
        return None

    def all(self) -> list[AgentConfig]:
        """Return all registered agent configs."""
        return list(self._configs.values())

    def load_from_yaml(self, path: Path) -> AgentConfig:
        """Load an agent config from a YAML file."""
        with path.open() as f:
            data = yaml.safe_load(f)
        config = AgentConfig.model_validate(data)
        self.register(config)
        return config

    def load_directory(self, directory: Path) -> list[AgentConfig]:
        """Load all agent configs from YAML files in a directory."""
        configs = []
        if not directory.exists():
            return configs
        for path in sorted(directory.glob("*.yaml")):
            config = self.load_from_yaml(path)
            configs.append(config)
        for path in sorted(directory.glob("*.yml")):
            config = self.load_from_yaml(path)
            configs.append(config)
        return configs

    def load_bundled(self) -> list[AgentConfig]:
        """Load bundled agent configs."""
        return self.load_directory(BUNDLED_DIR)

    def create_agent(self, config: AgentConfig, deps: Deps) -> Agent[Deps, str]:
        """Create a pydantic-ai Agent from config.

        Args:
            config: The agent configuration.
            deps: Dependencies to use.

        Returns:
            A configured pydantic-ai Agent.
        """
        from pydantic_ai import Agent, RunContext

        from ..settings import settings
        from ..tools import ALL_TOOLS

        # Determine model
        model = config.model or settings.get_model()

        # Determine system prompt
        system_prompt = config.system_prompt or "You are a helpful assistant. Be concise."

        # Create agent
        agent: Agent[Deps, str] = Agent(
            model,
            deps_type=Deps,
            system_prompt=system_prompt,
        )

        # Filter tools based on policy
        for tool_func in ALL_TOOLS:
            if config.can_use_tool(tool_func.__name__):
                agent.tool(tool_func)

        # Add dynamic instructions
        @agent.instructions
        async def context(ctx: RunContext[Deps]) -> str:
            """Build dynamic context."""
            lines = []

            # Agent identity
            lines.append(f"Agent: {config.identity.emoji} {config.identity.name}")

            # User
            user = ctx.deps.user
            roles = ", ".join(user.roles) if user.roles else "none"
            lines.append(f"User: {user.email} (roles: {roles})")

            # Project
            cur = await ctx.deps.workspace.projects.current()
            lines.append(f"Project: {cur[0]} at {cur[1]}" if cur else "No project selected.")

            # Page context
            if ctx.deps.current_page:
                lines.append(f"Viewing: {ctx.deps.current_page}")

            # Skills
            skills_prompt = ctx.deps.comms.skills.format_for_prompt()
            if skills_prompt:
                lines.append("")
                lines.append(skills_prompt)

            # Subagents (only for main agents)
            if not ctx.deps.is_subagent and ctx.deps.subagents:
                subagents_prompt = ctx.deps.subagents.list_for_prompt()
                if subagents_prompt:
                    lines.append("")
                    lines.append(subagents_prompt)

            return "\n".join(lines)

        return agent

    @classmethod
    def default(cls) -> AgentRegistry:
        """Create a registry with bundled configs loaded."""
        registry = cls()
        registry.load_bundled()
        return registry

    @classmethod
    def from_configs(cls, configs: Iterable[AgentConfig]) -> AgentRegistry:
        """Create a registry from a list of configs."""
        registry = cls()
        for config in configs:
            registry.register(config)
        return registry
