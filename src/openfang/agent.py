"""Agent factory, permissions, and instructions."""

from __future__ import annotations

from pydantic_ai import Agent, RunContext, ToolDefinition

from .deps import Deps
from .models import Role
from .tools import ALL_TOOLS

# =============================================================================
# TOOL PERMISSIONS
# =============================================================================

TOOL_PERMISSIONS: dict[str, set[str] | None] = {
    # File tools - developers only
    "file_read": {Role.DEVELOPER, Role.ADMIN},
    "file_write": {Role.DEVELOPER, Role.ADMIN},
    "file_list": {Role.DEVELOPER, Role.ADMIN},
    "file_search": {Role.DEVELOPER, Role.ADMIN},
    # Shell - admin only
    "shell_exec": {Role.ADMIN},
    # Web tools - all users
    "web_fetch": None,
    "web_browse": None,
    "web_screenshot": None,
    # Session tools - all users
    "web_session_start": None,
    "web_session_goto": None,
    "web_session_click": None,
    "web_session_type": None,
    "web_session_end": None,
    # Memory - all users
    "memory_set": None,
    "memory_get": None,
    "memory_delete": None,
    "memory_list": None,
    # Project tools - developers only
    "project_current": {Role.DEVELOPER, Role.ADMIN},
    "project_list": {Role.DEVELOPER, Role.ADMIN},
    "project_switch": {Role.DEVELOPER, Role.ADMIN},
    "project_register": {Role.ADMIN},
    # Cron tools - developers only
    "cron_create": {Role.DEVELOPER, Role.ADMIN},
    "cron_get": {Role.DEVELOPER, Role.ADMIN},
    "cron_list": {Role.DEVELOPER, Role.ADMIN},
    "cron_enable": {Role.DEVELOPER, Role.ADMIN},
    "cron_disable": {Role.DEVELOPER, Role.ADMIN},
    "cron_delete": {Role.ADMIN},
    # Telegram - all users
    "telegram_send": None,
}


async def filter_tools_by_permission(ctx: RunContext[Deps], tool_defs: list[ToolDefinition]) -> list[ToolDefinition]:
    """Filter tools based on user roles."""
    user = ctx.deps.user
    allowed = []
    for tool_def in tool_defs:
        required_roles = TOOL_PERMISSIONS.get(tool_def.name)
        if required_roles is None or user.roles & required_roles:
            allowed.append(tool_def)
    return allowed


# =============================================================================
# AGENT FACTORY
# =============================================================================


def create_agent(
    model: str = "openai:gpt-4o",
    system_prompt: str = "You are a helpful assistant. Be concise.",
) -> Agent[Deps, str]:
    """Create a configured agent with all tools registered."""
    agent: Agent[Deps, str] = Agent(
        model,
        deps_type=Deps,
        system_prompt=system_prompt,
        prepare_tools=filter_tools_by_permission,
    )

    # Register tools
    for tool_func in ALL_TOOLS:
        agent.tool(tool_func)

    # Register dynamic instructions
    @agent.instructions
    async def context(ctx: RunContext[Deps]) -> str:
        """Build dynamic context from user, page, project, permissions, and skills."""
        user = ctx.deps.user
        lines = []

        # User
        roles = ", ".join(user.roles) if user.roles else "none"
        lines.append(f"User: {user.email} (roles: {roles})")

        # Project
        cur = await ctx.deps.workspace.projects.current()
        lines.append(f"Project: {cur[0]} at {cur[1]}" if cur else "No project selected.")

        # Page
        if ctx.deps.current_page:
            lines.append(f"Viewing: {ctx.deps.current_page}")

        # Tools hint
        if user.is_admin:
            lines.append("Access: admin (all tools including shell)")
        elif user.has_role(Role.DEVELOPER):
            lines.append("Access: developer (file and project tools)")
        else:
            lines.append("Access: standard (web and memory tools)")

        # Skills
        skills_prompt = ctx.deps.comms.skills.format_for_prompt()
        if skills_prompt:
            lines.append("")
            lines.append(skills_prompt)

        return "\n".join(lines)

    return agent


# Default agent for convenience
default_agent = create_agent()
