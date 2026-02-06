"""Shared test fixtures and configuration.

Uses Fakes (simplified working implementations) over Mocks for better test reliability.
The InMemory* adapters are already effectively fakes - they work like the real
implementations but store data in memory.
"""

from __future__ import annotations

# Fail-safe: block accidental real LLM calls during tests
from pydantic_ai import models

models.ALLOW_MODEL_REQUESTS = False

from dataclasses import dataclass, field
from pathlib import Path  # noqa: TC003 - needed at runtime for type hints
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from openfang.capabilities import (
    InMemoryConversations,
    InMemoryCron,
    InMemoryMemory,
    LocalFiles,
)
from openfang.channels.models import ChannelAccount, ChannelInfo, ChannelStatus
from openfang.models import User
from openfang.types import Page, Result

if TYPE_CHECKING:
    from openfang.protocols import WebSession


# =============================================================================
# User fixtures
# =============================================================================


@pytest.fixture
def admin_user() -> User:
    """Admin user with all permissions."""
    return User(id=1, email="admin@test.com", roles={"admin"})


@pytest.fixture
def developer_user() -> User:
    """Developer user with file/project permissions."""
    return User(id=2, email="dev@test.com", roles={"developer"})


@pytest.fixture
def basic_user() -> User:
    """Basic user with minimal permissions."""
    return User(id=3, email="user@test.com", roles=set())


# =============================================================================
# Fake implementations
# =============================================================================


@dataclass
class FakeWebSession:
    """Fake browser session for testing."""

    current_url: str = "about:blank"
    current_title: str = "Blank"
    current_text: str = ""
    closed: bool = False

    async def goto(self, url: str) -> Page:
        self.current_url = url
        self.current_title = f"Page: {url}"
        self.current_text = f"Content of {url}"
        return Page(url=url, title=self.current_title, text=self.current_text, html=f"<html>{self.current_text}</html>")

    async def click(self, selector: str) -> Page:
        self.current_text = f"Clicked {selector}"
        return Page(
            url=self.current_url,
            title=self.current_title,
            text=self.current_text,
            html=f"<html>{self.current_text}</html>",
        )

    async def type(self, selector: str, text: str) -> None:
        pass  # No-op for fake

    async def screenshot(self) -> bytes:
        return b"fake-screenshot-png-data"

    async def close(self) -> None:
        self.closed = True


@dataclass
class FakeWeb:
    """Fake web access for testing."""

    responses: dict[str, str] = field(default_factory=dict)
    screenshots: dict[str, bytes] = field(default_factory=dict)

    async def fetch(self, url: str) -> str:
        return self.responses.get(url, f"Fetched content from {url}")

    async def browse(self, url: str) -> Page:
        text = self.responses.get(url, f"Browsed content from {url}")
        return Page(url=url, title=f"Page: {url}", text=text, html=f"<html>{text}</html>")

    async def screenshot(self, url: str) -> bytes:
        return self.screenshots.get(url, b"fake-screenshot-png-data")

    async def session(self) -> WebSession:
        return FakeWebSession()


@dataclass
class FakeShell:
    """Fake shell for testing - records commands without executing."""

    commands: list[tuple[str, Path | None]] = field(default_factory=list)
    responses: dict[str, Result] = field(default_factory=dict)
    default_result: Result = field(default_factory=lambda: Result(code=0, stdout="ok", stderr=""))

    async def exec(self, cmd: str, cwd: Path | None = None) -> Result:
        self.commands.append((cmd, cwd))
        return self.responses.get(cmd, self.default_result)


@dataclass
class FakeProjects:
    """Fake project registry for testing."""

    _projects: dict[str, Path] = field(default_factory=dict)
    _current: str | None = None

    async def current(self) -> tuple[str, Path] | None:
        if self._current and self._current in self._projects:
            return (self._current, self._projects[self._current])
        return None

    async def switch(self, project_id: str) -> Path:
        if project_id not in self._projects:
            raise KeyError(f"Project not found: {project_id}")
        self._current = project_id
        return self._projects[project_id]

    async def list(self) -> list[str]:
        return list(self._projects.keys())

    async def register(self, project_id: str, path: Path) -> None:
        self._projects[project_id] = path
        if self._current is None:
            self._current = project_id


@dataclass
class FakeTelegram:
    """Fake Telegram for testing - records messages without sending."""

    sent_messages: list[tuple[str | int, str]] = field(default_factory=list)
    sent_photos: list[tuple[str | int, bytes, str | None]] = field(default_factory=list)
    should_fail: bool = False

    async def send(self, chat_id: str | int, text: str) -> bool:
        if self.should_fail:
            return False
        self.sent_messages.append((chat_id, text))
        return True

    async def send_photo(self, chat_id: str | int, photo: bytes, caption: str | None = None) -> bool:
        if self.should_fail:
            return False
        self.sent_photos.append((chat_id, photo, caption))
        return True


class FakeChannel:
    """Fake channel implementation for testing."""

    def __init__(self, channel_id: str = "test", name: str = "Test Channel"):
        self._id = channel_id
        self._name = name
        self._started: set[str] = set()
        self._stopped: set[str] = set()

    @property
    def id(self) -> str:
        return self._id

    async def start(self, account_id: str) -> None:
        self._started.add(account_id)
        self._stopped.discard(account_id)

    async def stop(self, account_id: str) -> None:
        self._stopped.add(account_id)
        self._started.discard(account_id)

    async def send(self, account_id: str, target: str, text: str) -> bool:
        return account_id in self._started

    async def status(self, account_id: str) -> ChannelStatus:
        return ChannelStatus(
            account_id=account_id,
            channel_id=self._id,
            name=self._name,
            running=account_id in self._started,
            connected=account_id in self._started,
        )

    def info(self) -> ChannelInfo:
        return ChannelInfo(id=self._id, name=self._name, description="Fake channel for testing")


# Backwards-compatible alias
MockChannel = FakeChannel


# =============================================================================
# Capability fixtures (InMemory implementations are already fakes)
# =============================================================================


@pytest.fixture
def memory() -> InMemoryMemory:
    """In-memory key-value store (already a fake)."""
    return InMemoryMemory()


@pytest.fixture
def conversations() -> InMemoryConversations:
    """In-memory conversation store (already a fake)."""
    return InMemoryConversations()


@pytest.fixture
def cron() -> InMemoryCron:
    """In-memory cron scheduler (already a fake)."""
    return InMemoryCron()


@pytest.fixture
def files(tmp_path: Path) -> LocalFiles:
    """Local files scoped to temp directory."""
    return LocalFiles(root=tmp_path)


@pytest.fixture
def shell() -> FakeShell:
    """Fake shell that records commands."""
    return FakeShell()


@pytest.fixture
def web() -> FakeWeb:
    """Fake web access."""
    return FakeWeb()


@pytest.fixture
def projects(tmp_path: Path) -> FakeProjects:
    """Fake project registry with a default project."""
    fake = FakeProjects()
    fake._projects["default"] = tmp_path
    fake._current = "default"
    return fake


@pytest.fixture
def telegram() -> FakeTelegram:
    """Fake Telegram that records messages."""
    return FakeTelegram()


# =============================================================================
# Channel fixtures
# =============================================================================


@pytest.fixture
def mock_channel() -> FakeChannel:
    """Fake channel for testing (backwards-compatible name)."""
    return FakeChannel("telegram", "Telegram")


@pytest.fixture
def channel_account() -> ChannelAccount:
    """Sample channel account."""
    return ChannelAccount(
        id="acc-1",
        channel_id="telegram",
        name="Test Bot",
        config={"token": "test-token"},
    )


# =============================================================================
# Mock context fixture (for tool tests that need RunContext)
# =============================================================================


@pytest.fixture
def mock_ctx(admin_user: User) -> MagicMock:
    """Create a mock RunContext with mock deps for tool testing.

    Note: This uses MagicMock because pydantic-ai's RunContext is complex
    and tools need ctx.deps to be accessible. For integration tests,
    prefer using real Deps with fake adapters.
    """
    ctx = MagicMock()
    ctx.deps = MagicMock()
    ctx.deps.user = admin_user
    return ctx


@pytest.fixture
def mock_ctx_developer(developer_user: User) -> MagicMock:
    """Mock context with developer user."""
    ctx = MagicMock()
    ctx.deps = MagicMock()
    ctx.deps.user = developer_user
    return ctx


@pytest.fixture
def mock_ctx_basic(basic_user: User) -> MagicMock:
    """Mock context with basic user."""
    ctx = MagicMock()
    ctx.deps = MagicMock()
    ctx.deps.user = basic_user
    return ctx
