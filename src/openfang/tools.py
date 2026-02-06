"""Agent tools - all tool definitions."""

from __future__ import annotations

from collections.abc import Awaitable, Callable  # noqa: TC003 - needed at runtime for decorator
from functools import wraps
from pathlib import Path
from typing import ParamSpec, TypeVar

from pydantic_ai import BinaryContent, RunContext, ToolReturn

from .constants import (
    MAX_BROWSE_CHARS,
    MAX_FETCH_CHARS,
    MAX_GREP_RESULTS,
    MAX_LS_RESULTS,
    MAX_SESSION_CHARS,
    MAX_SHELL_OUTPUT,
)
from .deps import Deps  # noqa: TC001 - required at runtime for pydantic-ai introspection
from .helpers import format_page, truncate_text

P = ParamSpec("P")
T = TypeVar("T")


def tool_errors(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T | str]]:  # noqa: UP047
    """Decorator that catches exceptions and returns error strings for tools."""

    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T | str:
        try:
            return await func(*args, **kwargs)
        except FileNotFoundError as e:
            path = getattr(e, "filename", None) or "unknown"
            return f"Error: File not found: {path}"
        except PermissionError as e:
            path = getattr(e, "filename", None) or "unknown"
            return f"Error: Permission denied: {path}"
        except Exception as e:
            return f"Error: {e}"

    return wrapper


# =============================================================================
# TOOLS: Files
# =============================================================================


@tool_errors
async def file_read(ctx: RunContext[Deps], path: str) -> str:
    """Read a file.

    Args:
        path: File path relative to project root, or absolute path.
    """
    return await ctx.deps.storage.files.read(path)


@tool_errors
async def file_write(ctx: RunContext[Deps], path: str, content: str) -> str:
    """Write content to a file. Creates parent directories if needed.

    Args:
        path: File path relative to project root, or absolute path.
        content: The text content to write.
    """
    await ctx.deps.storage.files.write(path, content)
    return f"Wrote {len(content)} bytes to {path}"


@tool_errors
async def file_list(ctx: RunContext[Deps], glob: str = "**/*") -> str:
    """List files matching a glob pattern.

    Args:
        glob: Glob pattern like "*.py", "src/**/*.ts", or "**/*" for all files.
    """
    files = await ctx.deps.storage.files.list(glob)
    if not files:
        return "No files found"
    total = len(files)
    result = "\n".join(files[:MAX_LS_RESULTS])
    if total > MAX_LS_RESULTS:
        result += f"\n... ({total - MAX_LS_RESULTS} more files, {total} total)"
    return result


@tool_errors
async def file_search(ctx: RunContext[Deps], pattern: str, glob: str = "**/*") -> str:
    """Search file contents using regex.

    Args:
        pattern: Regular expression to search for.
        glob: Glob pattern to filter which files to search, e.g. "*.py".
    """
    matches = await ctx.deps.storage.files.search(pattern, glob)
    if not matches:
        return "No matches"
    total = len(matches)
    result = "\n".join(f"{m.path}:{m.line}: {m.text}" for m in matches[:MAX_GREP_RESULTS])
    if total > MAX_GREP_RESULTS:
        result += f"\n... ({total - MAX_GREP_RESULTS} more matches, {total} total)"
    return result


# =============================================================================
# TOOLS: Web (stateless)
# =============================================================================


@tool_errors
async def web_fetch(ctx: RunContext[Deps], url: str) -> str:
    """Fetch URL content as plain text (no JavaScript rendering).

    Args:
        url: The URL to fetch.
    """
    content = await ctx.deps.web_adapters.web.fetch(url)
    text, suffix = truncate_text(content, MAX_FETCH_CHARS)
    return text + suffix


@tool_errors
async def web_browse(ctx: RunContext[Deps], url: str) -> str:
    """Browse URL with full JavaScript rendering, return page text.

    Args:
        url: The URL to browse.
    """
    page = await ctx.deps.web_adapters.web.browse(url)
    return format_page(page, MAX_BROWSE_CHARS)


async def web_screenshot(ctx: RunContext[Deps], url: str) -> ToolReturn:
    """Take a screenshot of a URL.

    Args:
        url: The URL to screenshot.
    """
    try:
        data = await ctx.deps.web_adapters.web.screenshot(url)
        return ToolReturn(
            return_value=f"Screenshot captured ({len(data)} bytes)",
            content=[
                f"Screenshot of {url}:",
                BinaryContent(data=data, media_type="image/png"),
            ],
        )
    except Exception as e:
        return ToolReturn(return_value=f"Error: {e}")


# =============================================================================
# TOOLS: Web (sessions)
# =============================================================================


@tool_errors
async def web_session_start(ctx: RunContext[Deps]) -> str:
    """Start a new stateful browser session. Returns a session ID for subsequent calls."""
    session = await ctx.deps.web_adapters.web.session()
    sid = ctx.deps.new_session_id()
    ctx.deps.store_session(sid, session)
    return f"Session started: {sid}"


async def web_session_goto(ctx: RunContext[Deps], session_id: str, url: str) -> str:
    """Navigate a browser session to a URL.

    Args:
        session_id: Session ID from web_session_start.
        url: The URL to navigate to.
    """
    session = ctx.deps.get_session(session_id)
    if not session:
        return f"Error: Session not found: {session_id}. Use web_session_start first."
    try:
        page = await session.goto(url)
        return format_page(page, MAX_SESSION_CHARS, include_url=False)
    except Exception as e:
        return f"Error: {e}"


async def web_session_click(ctx: RunContext[Deps], session_id: str, selector: str) -> str:
    """Click an element in a browser session.

    Args:
        session_id: Session ID from web_session_start.
        selector: CSS selector for the element to click, e.g. "button.submit" or "#login".
    """
    session = ctx.deps.get_session(session_id)
    if not session:
        return f"Error: Session not found: {session_id}. Use web_session_start first."
    try:
        page = await session.click(selector)
        text, suffix = truncate_text(page.text, MAX_SESSION_CHARS)
        return f"Clicked. Title: {page.title}\n\n{text}{suffix}"
    except Exception as e:
        return f"Error: {e}"


async def web_session_type(ctx: RunContext[Deps], session_id: str, selector: str, text: str) -> str:
    """Type text into an input element in a browser session.

    Args:
        session_id: Session ID from web_session_start.
        selector: CSS selector for the input element, e.g. "input[name=email]" or "#password".
        text: The text to type into the element.
    """
    session = ctx.deps.get_session(session_id)
    if not session:
        return f"Error: Session not found: {session_id}. Use web_session_start first."
    try:
        await session.type(selector, text)
        return f"Typed into {selector}"
    except Exception as e:
        return f"Error: {e}"


async def web_session_end(ctx: RunContext[Deps], session_id: str) -> str:
    """Close a browser session and free its resources.

    Args:
        session_id: Session ID from web_session_start.
    """
    session = ctx.deps.remove_session(session_id)
    if not session:
        return f"Error: Session not found: {session_id}"
    try:
        await session.close()
        return f"Session closed: {session_id}"
    except Exception as e:
        return f"Error: {e}"


# =============================================================================
# TOOLS: Memory
# =============================================================================


async def memory_set(ctx: RunContext[Deps], key: str, value: str) -> str:
    """Store a value in persistent memory.

    Args:
        key: A unique key to store the value under.
        value: The text value to store.
    """
    await ctx.deps.storage.memory.set(key, value)
    return f"Stored: {key}"


async def memory_get(ctx: RunContext[Deps], key: str) -> str:
    """Retrieve a value from memory.

    Args:
        key: The key to retrieve.
    """
    value = await ctx.deps.storage.memory.get(key)
    return value if value else f"Not found: {key}"


async def memory_delete(ctx: RunContext[Deps], key: str) -> str:
    """Delete a value from memory.

    Args:
        key: The key to delete.
    """
    await ctx.deps.storage.memory.delete(key)
    return f"Deleted: {key}"


async def memory_list(ctx: RunContext[Deps], prefix: str = "") -> str:
    """List all memory keys, optionally filtered by prefix.

    Args:
        prefix: Only return keys starting with this prefix.
    """
    keys = await ctx.deps.storage.memory.keys(prefix)
    return "\n".join(keys) if keys else "No memories"


# =============================================================================
# TOOLS: Shell
# =============================================================================


@tool_errors
async def shell_exec(ctx: RunContext[Deps], cmd: str, cwd: str | None = None) -> str:
    """Execute a shell command (admin only).

    Args:
        cmd: The shell command to execute.
        cwd: Working directory for the command. Defaults to project root.
    """
    cwd_path = Path(cwd) if cwd else None
    result = await ctx.deps.workspace.shell.exec(cmd, cwd=cwd_path)
    output = result.stdout
    if result.stderr:
        output += f"\n[stderr]\n{result.stderr}"
    if not result.ok:
        output += f"\n[exit code: {result.code}]"
    text, suffix = truncate_text(output, MAX_SHELL_OUTPUT)
    return text + suffix


# =============================================================================
# TOOLS: Projects
# =============================================================================


async def project_current(ctx: RunContext[Deps]) -> str:
    """Get the currently active project."""
    cur = await ctx.deps.workspace.projects.current()
    if not cur:
        return "No project selected"
    return f"Project: {cur[0]}\nRoot: {cur[1]}"


async def project_list(ctx: RunContext[Deps]) -> str:
    """List all registered projects. Current project is marked with *."""
    ids = await ctx.deps.workspace.projects.list()
    if not ids:
        return "No projects registered"
    cur = await ctx.deps.workspace.projects.current()
    cur_id = cur[0] if cur else None
    return "\n".join(f"{'* ' if pid == cur_id else '  '}{pid}" for pid in ids)


async def project_switch(ctx: RunContext[Deps], project_id: str) -> str:
    """Switch to a different project. File and shell operations will use the new project root.

    Args:
        project_id: The project ID to switch to (from project_list).
    """
    try:
        await ctx.deps.switch_project(project_id)
        return f"Switched to: {project_id}"
    except KeyError:
        return f"Error: Project not found: {project_id}. Use project_list to see available projects."


async def project_register(ctx: RunContext[Deps], project_id: str, path: str) -> str:
    """Register a new project (admin only).

    Args:
        project_id: A unique identifier for the project.
        path: Absolute path to the project root directory.
    """
    try:
        p = Path(path).resolve()
        if not p.exists():
            return f"Error: Path does not exist: {path}"
        if not p.is_dir():
            return f"Error: Path is not a directory: {path}"
        await ctx.deps.workspace.projects.register(project_id, p)
        return f"Registered: {project_id} at {p}"
    except Exception as e:
        return f"Error: {e}"


# =============================================================================
# TOOLS: Cron
# =============================================================================


@tool_errors
async def cron_create(ctx: RunContext[Deps], schedule: str, task: str) -> str:
    """Create a scheduled cron job.

    Args:
        schedule: Cron expression like "0 9 * * *" (9am daily) or "*/15 * * * *" (every 15 min).
        task: Description of the task to run.
    """
    job = await ctx.deps.scheduling.cron.create(schedule, task, ctx.deps.user.id)
    return f"Created job {job.id}: '{task}' scheduled at '{schedule}'"


async def cron_get(ctx: RunContext[Deps], job_id: str) -> str:
    """Get details of a specific cron job.

    Args:
        job_id: The job ID from cron_list.
    """
    try:
        job = await ctx.deps.scheduling.cron.get(job_id)
        if not job:
            return f"Job not found: {job_id}"
        status = "enabled" if job.enabled else "disabled"
        return f"ID: {job.id}\nSchedule: {job.schedule}\nTask: {job.task}\nStatus: {status}"
    except Exception as e:
        return f"Error: {e}"


async def cron_list(ctx: RunContext[Deps]) -> str:
    """List all scheduled cron jobs for the current user."""
    try:
        jobs = await ctx.deps.scheduling.cron.list(ctx.deps.user.id)
        if not jobs:
            return "No scheduled jobs"
        lines = []
        for job in jobs:
            status = "enabled" if job.enabled else "disabled"
            lines.append(f"{job.id}: [{status}] {job.schedule} - {job.task}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


async def cron_enable(ctx: RunContext[Deps], job_id: str) -> str:
    """Enable a disabled cron job.

    Args:
        job_id: The job ID to enable.
    """
    try:
        if await ctx.deps.scheduling.cron.enable(job_id):
            return f"Enabled job {job_id}"
        return f"Job not found: {job_id}"
    except Exception as e:
        return f"Error: {e}"


async def cron_disable(ctx: RunContext[Deps], job_id: str) -> str:
    """Disable a cron job without deleting it.

    Args:
        job_id: The job ID to disable.
    """
    try:
        if await ctx.deps.scheduling.cron.disable(job_id):
            return f"Disabled job {job_id}"
        return f"Job not found: {job_id}"
    except Exception as e:
        return f"Error: {e}"


async def cron_delete(ctx: RunContext[Deps], job_id: str) -> str:
    """Permanently delete a cron job (admin only).

    Args:
        job_id: The job ID to delete.
    """
    try:
        if await ctx.deps.scheduling.cron.delete(job_id):
            return f"Deleted job {job_id}"
        return f"Job not found: {job_id}"
    except Exception as e:
        return f"Error: {e}"


# =============================================================================
# TOOLS: Telegram
# =============================================================================


async def telegram_send(ctx: RunContext[Deps], chat_id: str, message: str) -> str:
    """Send a text message via Telegram.

    Args:
        chat_id: The Telegram chat ID to send to.
        message: The message text.
    """
    try:
        channel = ctx.deps.comms.channels.get_channel("telegram")
        if not channel:
            return "Telegram channel not configured"
        success = await channel.send("default", chat_id, message)
        if success:
            return f"Message sent to {chat_id}"
        return "Failed to send message (check telegram token is configured)"
    except Exception as e:
        return f"Error: {e}"


# =============================================================================
# TOOLS: Discord
# =============================================================================


async def discord_send(ctx: RunContext[Deps], channel_id: str, message: str) -> str:
    """Send a text message via Discord.

    Args:
        channel_id: The Discord channel ID or user ID to send to.
        message: The message text.
    """
    try:
        channel = ctx.deps.comms.channels.get_channel("discord")
        if not channel:
            return "Discord channel not configured"
        success = await channel.send("default", channel_id, message)
        if success:
            return f"Message sent to {channel_id}"
        return "Failed to send message (check discord token is configured)"
    except Exception as e:
        return f"Error: {e}"


# =============================================================================
# TOOL REGISTRY
# =============================================================================

from .subagents import SUBAGENT_TOOLS  # noqa: E402 - late import to avoid circular dependency

ALL_TOOLS = [
    # Files
    file_read,
    file_write,
    file_list,
    file_search,
    # Web (stateless)
    web_fetch,
    web_browse,
    web_screenshot,
    # Web (sessions)
    web_session_start,
    web_session_goto,
    web_session_click,
    web_session_type,
    web_session_end,
    # Memory
    memory_set,
    memory_get,
    memory_delete,
    memory_list,
    # Shell
    shell_exec,
    # Projects
    project_current,
    project_list,
    project_switch,
    project_register,
    # Cron
    cron_create,
    cron_get,
    cron_list,
    cron_enable,
    cron_disable,
    cron_delete,
    # Telegram
    telegram_send,
    # Discord
    discord_send,
    # Subagents
    *SUBAGENT_TOOLS,
]
