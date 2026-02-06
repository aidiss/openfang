"""Deps container - all adapters for an agent.

Adapters are organized into logical groups:
- storage: files, memory, conversations (data persistence)
- web: browser-based operations and sessions
- workspace: shell, projects (local environment)
- scheduling: cron jobs
- comms: channels, skills (communication and capabilities)
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from .capabilities import (
    InMemoryConversations,
    InMemoryCron,
    InMemoryMemory,
    LocalFiles,
    LocalProjects,
    LocalShell,
    PlaywrightWeb,
)
from .channels import ChannelRegistry
from .skills import SkillRegistry

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from .models import User
    from .protocols import Channels, Conversations, Cron, Files, Memory, Projects, Shell, Skills, Web, WebSession
    from .subagents import SubagentExecutor, SubagentRegistry


# =============================================================================
# Adapter Groups
# =============================================================================


@dataclass
class StorageAdapters:
    """Data persistence adapters."""

    files: Files
    memory: Memory
    conversations: Conversations

    @classmethod
    def default(cls, root: Path, conversations: Conversations | None = None) -> StorageAdapters:
        return cls(
            files=LocalFiles(root),
            memory=InMemoryMemory(),
            conversations=conversations or InMemoryConversations(),
        )


@dataclass
class WebAdapters:
    """Browser-based operations with session management."""

    web: Web
    _sessions: dict[str, WebSession] = field(default_factory=dict)
    _session_counter: int = 0

    @classmethod
    def default(cls) -> WebAdapters:
        return cls(web=PlaywrightWeb())

    def new_session_id(self) -> str:
        self._session_counter += 1
        return f"session-{self._session_counter}"

    def get_session(self, session_id: str) -> WebSession | None:
        return self._sessions.get(session_id)

    def store_session(self, session_id: str, session: WebSession) -> None:
        self._sessions[session_id] = session

    def remove_session(self, session_id: str) -> WebSession | None:
        return self._sessions.pop(session_id, None)

    async def close(self) -> None:
        for session in self._sessions.values():
            await session.close()
        self._sessions.clear()


@dataclass
class WorkspaceAdapters:
    """Local environment adapters."""

    shell: Shell
    projects: Projects

    @classmethod
    def default(cls, root: Path) -> WorkspaceAdapters:
        return cls(shell=LocalShell(root), projects=LocalProjects())


@dataclass
class SchedulingAdapters:
    """Time-based operations."""

    cron: Cron

    @classmethod
    def default(cls, cron: Cron | None = None) -> SchedulingAdapters:
        return cls(cron=cron or InMemoryCron())


@dataclass
class CommsAdapters:
    """Communication and capabilities."""

    channels: Channels
    skills: Skills

    @classmethod
    def default(cls) -> CommsAdapters:
        return cls(channels=ChannelRegistry.default(), skills=SkillRegistry.default())


# =============================================================================
# Deps Container
# =============================================================================


@dataclass
class Deps:
    """All adapters + user context for an agent."""

    user: User
    storage: StorageAdapters
    web_adapters: WebAdapters
    workspace: WorkspaceAdapters
    scheduling: SchedulingAdapters
    comms: CommsAdapters
    current_page: str | None = None
    conversation_id: str | None = None

    # Subagent context
    is_subagent: bool = False
    """True if this is a subagent execution (prevents recursive spawning)."""

    parent_run_id: str | None = None
    """If subagent, the parent's run ID."""

    subagents: SubagentRegistry | None = None
    """Registry of available subagents."""

    subagent_executor: SubagentExecutor | None = None
    """Executor for spawning subagents."""

    # Session management delegates to web_adapters
    def new_session_id(self) -> str:
        return self.web_adapters.new_session_id()

    def get_session(self, session_id: str) -> WebSession | None:
        return self.web_adapters.get_session(session_id)

    def store_session(self, session_id: str, session: WebSession) -> None:
        self.web_adapters.store_session(session_id, session)

    def remove_session(self, session_id: str) -> WebSession | None:
        return self.web_adapters.remove_session(session_id)

    async def switch_project(self, project_id: str) -> None:
        """Switch to a different project, updating file/shell roots."""
        path = await self.workspace.projects.switch(project_id)
        self.storage = StorageAdapters(
            files=LocalFiles(path),
            memory=self.storage.memory,
            conversations=self.storage.conversations,
        )
        self.workspace = WorkspaceAdapters(
            shell=LocalShell(path),
            projects=self.workspace.projects,
        )

    async def close(self) -> None:
        await self.web_adapters.close()


# =============================================================================
# Factory
# =============================================================================


@asynccontextmanager
async def create_deps(
    user: User,
    root: Path | None = None,
    conversations: Conversations | None = None,
    cron: Cron | None = None,
    current_page: str | None = None,
    conversation_id: str | None = None,
    enable_subagents: bool = True,
) -> AsyncIterator[Deps]:
    """Create Deps with sensible defaults. Use as async context manager.

    Args:
        user: User context for the agent.
        root: Root directory for file operations.
        conversations: Conversation storage adapter.
        cron: Cron adapter.
        current_page: Current page context.
        conversation_id: Current conversation ID.
        enable_subagents: Whether to enable subagent delegation.
    """
    from .subagents import SubagentExecutor, SubagentRegistry

    root = root or Path.cwd()

    # Initialize subagent system if enabled
    subagents = SubagentRegistry.default() if enable_subagents else None
    subagent_executor = SubagentExecutor() if enable_subagents else None

    deps = Deps(
        user=user,
        storage=StorageAdapters.default(root, conversations),
        web_adapters=WebAdapters.default(),
        workspace=WorkspaceAdapters.default(root),
        scheduling=SchedulingAdapters.default(cron),
        comms=CommsAdapters.default(),
        current_page=current_page,
        conversation_id=conversation_id,
        subagents=subagents,
        subagent_executor=subagent_executor,
    )
    try:
        yield deps
    finally:
        await deps.close()
