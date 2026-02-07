"""Protocol definitions (ports) for all adapters."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from pathlib import Path

    from pydantic_ai.messages import ModelMessage

    from .channels.models import InboundMessage
    from .models import CronJob
    from .types import Match, Page, Result

    # Type alias for message handler callback
    MessageHandler = Callable[[InboundMessage], Awaitable[None]]


@runtime_checkable
class Files(Protocol):
    """File operations scoped to a root directory."""

    root: Path

    async def read(self, path: str) -> str:
        """Read file contents as text.

        Args:
            path: Relative to root, or absolute path.
        """
        ...

    async def write(self, path: str, content: str) -> None:
        """Write content to file, creating parent directories if needed.

        Args:
            path: Relative to root, or absolute path.
            content: Text content to write.
        """
        ...

    async def list(self, pattern: str = "**/*") -> list[str]:
        """List files matching a glob pattern.

        Args:
            pattern: Glob pattern like "*.py" or "**/*.ts".
        """
        ...

    async def search(self, pattern: str, file_glob: str = "**/*") -> list[Match]:
        """Search file contents using regex.

        Args:
            pattern: Regular expression to search for.
            file_glob: Glob pattern to filter which files to search.
        """
        ...


@runtime_checkable
class WebSession(Protocol):
    """Stateful browser session."""

    async def goto(self, url: str) -> Page:
        """Navigate to a URL and return the page content."""
        ...

    async def click(self, selector: str) -> Page:
        """Click an element and return the updated page content."""
        ...

    async def type(self, selector: str, text: str) -> None:
        """Type text into an input element."""
        ...

    async def screenshot(self) -> bytes:
        """Take a screenshot of the current page."""
        ...

    async def close(self) -> None:
        """Close the browser session and free resources."""
        ...


@runtime_checkable
class Web(Protocol):
    """Web access - stateless + session factory."""

    async def fetch(self, url: str) -> str:
        """Fetch URL content as plain text (no JavaScript rendering)."""
        ...

    async def browse(self, url: str) -> Page:
        """Browse URL with full JavaScript rendering."""
        ...

    async def screenshot(self, url: str) -> bytes:
        """Take a screenshot of a URL."""
        ...

    async def session(self) -> WebSession:
        """Create a new stateful browser session."""
        ...


@runtime_checkable
class Memory(Protocol):
    """Key-value store."""

    async def get(self, key: str) -> str | None:
        """Retrieve a value by key, or None if not found."""
        ...

    async def set(self, key: str, value: str) -> None:
        """Store a value under the given key."""
        ...

    async def delete(self, key: str) -> None:
        """Delete a key from memory."""
        ...

    async def keys(self, prefix: str = "") -> list[str]:
        """List all keys, optionally filtered by prefix."""
        ...


@runtime_checkable
class Shell(Protocol):
    """Command execution."""

    async def exec(self, cmd: str, cwd: Path | None = None) -> Result:
        """Execute a shell command and return the result."""
        ...


@runtime_checkable
class Projects(Protocol):
    """Project management."""

    async def current(self) -> tuple[str, Path] | None:
        """Get the current project ID and path, or None if none selected."""
        ...

    async def switch(self, project_id: str) -> Path:
        """Switch to a project and return its root path."""
        ...

    async def list(self) -> list[str]:
        """List all registered project IDs."""
        ...

    async def register(self, project_id: str, path: Path) -> None:
        """Register a new project with the given ID and path."""
        ...


@runtime_checkable
class Sessions(Protocol):
    """Store and retrieve session message histories (transcripts)."""

    async def get(self, session_id: str) -> list[ModelMessage]:
        """Get all messages for a session."""
        ...

    async def save(self, session_id: str, messages: list[ModelMessage]) -> None:
        """Save (replace) all messages for a session."""
        ...

    async def append(self, session_id: str, messages: list[ModelMessage]) -> None:
        """Append messages to a session."""
        ...

    async def delete(self, session_id: str) -> None:
        """Delete a session and all its messages."""
        ...

    async def list(self, user_id: int | None = None) -> list[str]:
        """List all session IDs, optionally filtered by user."""
        ...


@runtime_checkable
class Cron(Protocol):
    """Schedule and manage cron jobs."""

    async def create(self, schedule: str, task: str, user_id: int | None = None) -> CronJob:
        """Create a new scheduled job."""
        ...

    async def get(self, job_id: str) -> CronJob | None:
        """Get a job by ID, or None if not found."""
        ...

    async def list(self, user_id: int | None = None) -> list[CronJob]:
        """List all jobs, optionally filtered by user."""
        ...

    async def delete(self, job_id: str) -> bool:
        """Delete a job. Returns True if deleted, False if not found."""
        ...

    async def enable(self, job_id: str) -> bool:
        """Enable a job. Returns True if enabled, False if not found."""
        ...

    async def disable(self, job_id: str) -> bool:
        """Disable a job. Returns True if disabled, False if not found."""
        ...


@runtime_checkable
class Skills(Protocol):
    """Skill registry and discovery."""

    @property
    def skills(self) -> dict[str, Skill]:
        """All registered skills."""
        ...

    def get(self, name: str) -> Skill | None:
        """Get a skill by name, or None if not found."""
        ...

    def is_eligible(self, skill: Skill) -> bool:
        """Check if a skill's requirements are met."""
        ...

    def eligible_skills(self) -> list[Skill]:
        """List all skills whose requirements are met."""
        ...

    def invocable_skills(self) -> list[Skill]:
        """List skills that can be invoked by users."""
        ...

    def model_skills(self) -> list[Skill]:
        """List skills available to the model."""
        ...

    def format_for_prompt(self, skills: list[Skill] | None = None) -> str:
        """Format skills for inclusion in the system prompt."""
        ...

    def load_from_dir(self, path: Path, source: str = "custom") -> None:
        """Load skills from a directory."""
        ...


@runtime_checkable
class Channel(Protocol):
    """External messaging platform connector."""

    id: str  # "telegram", "discord", "slack"

    async def start(self, account_id: str) -> None:
        """Start the channel for an account."""
        ...

    async def stop(self, account_id: str) -> None:
        """Stop the channel for an account."""
        ...

    async def send(self, account_id: str, target: str, text: str) -> bool:
        """Send a message. Returns True on success."""
        ...

    async def status(self, account_id: str) -> ChannelStatus:
        """Get the status of an account."""
        ...

    def info(self) -> ChannelInfo:
        """Get channel metadata."""
        ...

    def set_message_handler(self, handler: MessageHandler | None) -> None:
        """Set callback for inbound messages.

        Args:
            handler: Async callback called with InboundMessage, or None to clear.
        """
        ...


@runtime_checkable
class Channels(Protocol):
    """Channel registry - manages all channel implementations."""

    def get_channel(self, channel_id: str) -> Channel | None:
        """Get a channel by ID, or None if not found."""
        ...

    def list_channels(self) -> list[ChannelInfo]:
        """List all registered channels."""
        ...

    async def add_account(self, account: ChannelAccount) -> None:
        """Add an account to a channel."""
        ...

    async def remove_account(self, channel_id: str, account_id: str) -> None:
        """Remove an account from a channel."""
        ...

    async def list_accounts(self, channel_id: str | None = None) -> list[ChannelAccount]:
        """List accounts, optionally filtered by channel."""
        ...

    async def start_account(self, channel_id: str, account_id: str) -> None:
        """Start an account on a channel."""
        ...

    async def stop_account(self, channel_id: str, account_id: str) -> None:
        """Stop an account on a channel."""
        ...

    async def start_all(self) -> None:
        """Start all configured channel accounts."""
        ...

    async def stop_all(self) -> None:
        """Stop all running channel accounts."""
        ...

    async def status(self) -> list[ChannelStatus]:
        """Get status of all accounts across all channels."""
        ...

    def set_message_handler(self, handler: MessageHandler | None) -> None:
        """Set message handler callback on all registered channels.

        Args:
            handler: Async callback called with InboundMessage, or None to clear.
        """
        ...


if TYPE_CHECKING:
    from .channels.models import ChannelAccount, ChannelInfo, ChannelStatus
    from .skills.models import Skill
