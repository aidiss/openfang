"""Subagent tools - delegation and management."""

from __future__ import annotations

from pydantic_ai import RunContext

from ..deps import Deps


async def subagent_delegate(
    ctx: RunContext[Deps],
    subagent_id: str,
    task: str,
    timeout_seconds: int = 300,
) -> str:
    """Delegate a task to a specialized subagent.

    Use this to hand off specific tasks to specialists like code-analyzer,
    web-researcher, or summarizer. The subagent will complete the task
    and return its result.

    Args:
        subagent_id: ID of the subagent to delegate to (from subagent_list).
        task: Clear description of the task for the subagent.
        timeout_seconds: Maximum time to wait for completion (default 300s).

    Returns:
        The subagent's response, or an error message.
    """
    # Check if we're already a subagent (prevent recursion)
    if ctx.deps.is_subagent:
        return "Error: Subagents cannot delegate to other subagents."

    # Check if subagent system is available
    if not ctx.deps.subagents or not ctx.deps.subagent_executor:
        return "Error: Subagent system not configured."

    # Get the subagent spec
    spec = ctx.deps.subagents.get(subagent_id)
    if not spec:
        available = ", ".join(s.id for s in ctx.deps.subagents.all())
        return f"Error: Unknown subagent '{subagent_id}'. Available: {available}"

    # Execute the subagent
    result = await ctx.deps.subagent_executor.run_sync(
        spec=spec,
        task=task,
        deps=ctx.deps,
        timeout_seconds=timeout_seconds,
    )

    # Format result
    if result.status == "success":
        return f"[{spec.name}]\n\n{result.output}"
    elif result.status == "timeout":
        return f"Error: {spec.name} timed out after {timeout_seconds}s"
    else:
        return f"Error: {spec.name} failed - {result.error}"


async def subagent_list(ctx: RunContext[Deps]) -> str:
    """List available specialized subagents.

    Returns a list of subagent IDs with their descriptions.
    Use these IDs with subagent_delegate to hand off tasks.
    """
    if not ctx.deps.subagents:
        return "No subagents configured."

    specs = ctx.deps.subagents.all()
    if not specs:
        return "No subagents available."

    lines = ["Available subagents:", ""]
    for spec in specs:
        tools_info = ""
        if spec.tools:
            tools_info = f" (tools: {', '.join(spec.tools[:3])}{'...' if len(spec.tools) > 3 else ''})"
        elif spec.denied_tools:
            tools_info = " (some tools restricted)"
        lines.append(f"- **{spec.id}**: {spec.description}{tools_info}")

    return "\n".join(lines)


# Export list of subagent tools
SUBAGENT_TOOLS = [
    subagent_delegate,
    subagent_list,
]
