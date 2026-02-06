"""Tests for adapter implementations."""

import pytest

from openfang.capabilities import InMemoryConversations, InMemoryMemory, LocalFiles


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
class TestInMemoryConversations:
    @pytest.fixture
    def convos(self):
        return InMemoryConversations()

    async def test_get_nonexistent(self, convos):
        assert await convos.get("missing") == []

    async def test_save_and_get(self, convos):
        messages = [{"role": "user", "content": "hi"}]
        await convos.save("conv-1", messages)
        assert await convos.get("conv-1") == messages

    async def test_append(self, convos):
        await convos.save("conv-1", [{"role": "user", "content": "hi"}])
        await convos.append("conv-1", [{"role": "assistant", "content": "hello"}])

        messages = await convos.get("conv-1")
        assert len(messages) == 2

    async def test_append_to_new(self, convos):
        await convos.append("new-conv", [{"role": "user", "content": "hi"}])
        assert len(await convos.get("new-conv")) == 1

    async def test_delete(self, convos):
        await convos.save("conv-1", [{"role": "user", "content": "hi"}])
        await convos.delete("conv-1")
        assert await convos.get("conv-1") == []

    async def test_list_all(self, convos):
        await convos.save("conv-1", [])
        await convos.save("conv-2", [])
        assert sorted(await convos.list()) == ["conv-1", "conv-2"]

    async def test_list_by_user(self, convos):
        await convos.save("conv-1", [])
        await convos.save("conv-2", [])
        convos.associate_user("conv-1", user_id=42)

        assert await convos.list(user_id=42) == ["conv-1"]
        assert await convos.list(user_id=999) == []

    async def test_delete_removes_user_association(self, convos):
        await convos.save("conv-1", [])
        convos.associate_user("conv-1", user_id=42)
        await convos.delete("conv-1")

        assert await convos.list(user_id=42) == []
