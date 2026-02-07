"""Integration tests for chat flow."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from openfang.capabilities import InMemorySessions
from openfang.chat import chat, start_session
from openfang.deps import (
    CommsAdapters,
    Deps,
    SchedulingAdapters,
    StorageAdapters,
    WebAdapters,
    WorkspaceAdapters,
)
from openfang.models import User


@pytest.fixture
def mock_user():
    return User(id=1, email="test@example.com", roles={"developer"})


@pytest.fixture
def deps(mock_user, tmp_path):
    """Create a real Deps object with in-memory adapters."""
    return Deps(
        user=mock_user,
        storage=StorageAdapters.default(tmp_path, sessions=InMemorySessions()),
        web_adapters=WebAdapters.default(),
        workspace=WorkspaceAdapters.default(tmp_path),
        scheduling=SchedulingAdapters.default(),
        comms=CommsAdapters.default(),
    )


@pytest.fixture
def mock_agent_result():
    """Create a mock agent result."""
    result = MagicMock()
    result.output = "Hello! How can I help you?"
    result.new_messages.return_value = [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "Hello! How can I help you?"},
    ]
    return result


@pytest.mark.asyncio
class TestChatFlow:
    """Test end-to-end chat flow."""

    async def test_start_session(self, deps):
        await start_session(deps, "session-123")

        assert deps.session_id == "session-123"
        # User should be associated with session
        user_sessions = await deps.storage.sessions.list(user_id=deps.user.id)
        assert "session-123" in user_sessions

    async def test_chat_saves_messages(self, deps, mock_agent_result):
        deps.session_id = "test-session"

        with patch("openfang.agent.default_agent") as mock_agent:
            mock_agent.run = AsyncMock(return_value=mock_agent_result)

            response = await chat(deps, "hi")

        assert response == "Hello! How can I help you?"

        # Messages should be saved
        messages = await deps.storage.sessions.get("test-session")
        assert len(messages) == 2

    async def test_chat_loads_history(self, deps, mock_agent_result):
        session_id = "history-test-session"
        deps.session_id = session_id

        # Pre-populate some history
        existing = [
            {"role": "user", "content": "previous message"},
            {"role": "assistant", "content": "previous response"},
        ]
        await deps.storage.sessions.save(session_id, existing)

        # Capture what history is passed to agent.run
        captured_history = None

        async def capture_run(*args, **kwargs):
            nonlocal captured_history
            # Copy the list at call time since it may be mutated later
            captured_history = list(kwargs.get("message_history", []))
            return mock_agent_result

        with patch("openfang.agent.default_agent") as mock_agent:
            mock_agent.run = capture_run

            await chat(deps, "new message")

            # Agent should have received the existing history
            assert captured_history == existing

    async def test_chat_without_session_id(self, deps, mock_agent_result):
        # No session_id set
        deps.session_id = None

        with patch("openfang.agent.default_agent") as mock_agent:
            mock_agent.run = AsyncMock(return_value=mock_agent_result)

            response = await chat(deps, "hi")

        assert response == "Hello! How can I help you?"
        # No history should be loaded or saved
        mock_agent.run.assert_called_once()
        call_kwargs = mock_agent.run.call_args.kwargs
        assert call_kwargs["message_history"] is None

    async def test_chat_appends_to_existing(self, deps, mock_agent_result):
        deps.session_id = "test-session"

        # First turn
        existing = [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}]
        await deps.storage.sessions.save("test-session", existing)

        with patch("openfang.agent.default_agent") as mock_agent:
            mock_agent.run = AsyncMock(return_value=mock_agent_result)

            await chat(deps, "follow up")

        # Should have 4 messages now (2 existing + 2 new)
        messages = await deps.storage.sessions.get("test-session")
        assert len(messages) == 4


@pytest.mark.asyncio
class TestDepsIntegration:
    """Test Deps object with real adapters."""

    async def test_deps_with_files(self, deps, tmp_path):
        # Write and read a file
        await deps.storage.files.write("test.txt", "hello world")
        content = await deps.storage.files.read("test.txt")
        assert content == "hello world"

    async def test_deps_with_memory(self, deps):
        await deps.storage.memory.set("key", "value")
        assert await deps.storage.memory.get("key") == "value"

    async def test_deps_with_sessions(self, deps):
        messages = [{"role": "user", "content": "test"}]
        await deps.storage.sessions.save("session-1", messages)

        retrieved = await deps.storage.sessions.get("session-1")
        assert retrieved == messages
