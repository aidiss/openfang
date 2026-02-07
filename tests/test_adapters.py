"""Tests for adapter implementations."""

import pytest
from pydantic_ai.messages import ModelRequest, ModelResponse, TextPart, UserPromptPart

from openfang.capabilities import FileSessions, InMemoryMemory, InMemorySessions, LocalFiles


@pytest.mark.asyncio
class TestInMemoryMemory:
    @pytest.fixture
    def memory(self):
        return InMemoryMemory()

    async def test_get_nonexistent(self, memory):
        assert await memory.get("missing") is None

    async def test_set_and_get(self, memory):
        await memory.set("key", "value")
        assert await memory.get("key") == "value"

    async def test_delete(self, memory):
        await memory.set("key", "value")
        await memory.delete("key")
        assert await memory.get("key") is None

    async def test_delete_nonexistent(self, memory):
        await memory.delete("missing")  # Should not raise

    async def test_keys_empty(self, memory):
        assert await memory.keys() == []

    async def test_keys_with_prefix(self, memory):
        await memory.set("user:1", "alice")
        await memory.set("user:2", "bob")
        await memory.set("config:theme", "dark")

        assert sorted(await memory.keys("user:")) == ["user:1", "user:2"]
        assert await memory.keys("config:") == ["config:theme"]
        assert len(await memory.keys()) == 3


@pytest.mark.asyncio
class TestLocalFiles:
    @pytest.fixture
    def files(self, tmp_path):
        return LocalFiles(root=tmp_path)

    async def test_write_and_read(self, files, tmp_path):
        await files.write("test.txt", "hello world")
        content = await files.read("test.txt")
        assert content == "hello world"

    async def test_write_creates_dirs(self, files, tmp_path):
        await files.write("nested/deep/file.txt", "content")
        assert (tmp_path / "nested/deep/file.txt").exists()

    async def test_list_files(self, files, tmp_path):
        await files.write("a.txt", "a")
        await files.write("b.txt", "b")
        await files.write("sub/c.txt", "c")

        all_files = await files.list()
        assert "a.txt" in all_files
        assert "b.txt" in all_files

    async def test_search(self, files, tmp_path):
        await files.write("code.py", "def hello():\n    return 'world'")
        await files.write("other.py", "x = 1")

        matches = await files.search(r"def \w+")
        assert len(matches) == 1
        assert matches[0].path == "code.py"
        assert matches[0].line == 1
        assert "def hello" in matches[0].text


@pytest.mark.asyncio
class TestInMemorySessions:
    @pytest.fixture
    def sessions(self):
        return InMemorySessions()

    async def test_get_nonexistent(self, sessions):
        assert await sessions.get("missing") == []

    async def test_save_and_get(self, sessions):
        messages = [{"role": "user", "content": "hi"}]
        await sessions.save("session-1", messages)
        assert await sessions.get("session-1") == messages

    async def test_append(self, sessions):
        await sessions.save("session-1", [{"role": "user", "content": "hi"}])
        await sessions.append("session-1", [{"role": "assistant", "content": "hello"}])

        messages = await sessions.get("session-1")
        assert len(messages) == 2

    async def test_append_to_new(self, sessions):
        await sessions.append("new-session", [{"role": "user", "content": "hi"}])
        assert len(await sessions.get("new-session")) == 1

    async def test_delete(self, sessions):
        await sessions.save("session-1", [{"role": "user", "content": "hi"}])
        await sessions.delete("session-1")
        assert await sessions.get("session-1") == []

    async def test_list_all(self, sessions):
        await sessions.save("session-1", [])
        await sessions.save("session-2", [])
        assert sorted(await sessions.list()) == ["session-1", "session-2"]

    async def test_list_by_user(self, sessions):
        await sessions.save("session-1", [])
        await sessions.save("session-2", [])
        sessions.associate_user("session-1", user_id=42)

        assert await sessions.list(user_id=42) == ["session-1"]
        assert await sessions.list(user_id=999) == []

    async def test_delete_removes_user_association(self, sessions):
        await sessions.save("session-1", [])
        sessions.associate_user("session-1", user_id=42)
        await sessions.delete("session-1")

        assert await sessions.list(user_id=42) == []


@pytest.mark.asyncio
class TestFileSessions:
    """Tests for file-based JSONL session storage."""

    @pytest.fixture
    def sessions(self, tmp_path):
        return FileSessions(tmp_path)

    @pytest.fixture
    def sample_messages(self):
        """Create sample ModelMessage objects for testing."""
        return [
            ModelRequest(parts=[UserPromptPart(content="Hello")]),
            ModelResponse(parts=[TextPart(content="Hi there!")]),
        ]

    async def test_get_nonexistent(self, sessions):
        assert await sessions.get("missing") == []

    async def test_save_and_get(self, sessions, sample_messages):
        await sessions.save("session-1", sample_messages)
        retrieved = await sessions.get("session-1")

        assert len(retrieved) == 2
        # Check message types preserved
        assert retrieved[0].kind == "request"
        assert retrieved[1].kind == "response"

    async def test_append(self, sessions, sample_messages):
        # Save initial messages
        await sessions.save("session-1", sample_messages[:1])

        # Append more
        await sessions.append("session-1", sample_messages[1:])

        retrieved = await sessions.get("session-1")
        assert len(retrieved) == 2

    async def test_append_to_new(self, sessions, sample_messages):
        # Append to non-existent session creates it
        await sessions.append("new-session", sample_messages)
        assert len(await sessions.get("new-session")) == 2

    async def test_delete(self, sessions, sample_messages):
        await sessions.save("session-1", sample_messages)
        await sessions.delete("session-1")
        assert await sessions.get("session-1") == []

    async def test_list_all(self, sessions, sample_messages):
        await sessions.save("session-1", sample_messages)
        await sessions.save("session-2", sample_messages)

        session_list = await sessions.list()
        assert "session-1" in session_list
        assert "session-2" in session_list

    async def test_file_persistence(self, tmp_path, sample_messages):
        # Save with one instance
        sessions1 = FileSessions(tmp_path)
        await sessions1.save("persistent", sample_messages)

        # Read with new instance (simulates restart)
        sessions2 = FileSessions(tmp_path)
        retrieved = await sessions2.get("persistent")

        assert len(retrieved) == 2
        assert retrieved[0].kind == "request"

    async def test_sanitizes_session_id(self, sessions, sample_messages):
        # Session keys contain colons
        session_key = "telegram:bot:dm:123456"
        await sessions.save(session_key, sample_messages)

        # Should be retrievable
        retrieved = await sessions.get(session_key)
        assert len(retrieved) == 2

    async def test_list_ignores_user_id(self, sessions, sample_messages):
        # FileSessions doesn't support user filtering
        await sessions.save("session-1", sample_messages)

        # user_id parameter is ignored, returns all
        all_sessions = await sessions.list(user_id=42)
        assert "session-1" in all_sessions
