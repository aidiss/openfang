"""Tests for agent tools."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from openfang.models import CronJob
from openfang.tools import (
    cron_create,
    cron_delete,
    cron_disable,
    cron_enable,
    cron_get,
    cron_list,
    file_list,
    file_read,
    file_search,
    file_write,
    memory_delete,
    memory_get,
    memory_list,
    memory_set,
    project_current,
    project_list,
    project_register,
    project_switch,
    shell_exec,
)
from openfang.types import Match, Result


@pytest.fixture
def mock_ctx():
    """Create a mock RunContext with mock deps."""
    ctx = MagicMock()
    ctx.deps = MagicMock()
    ctx.deps.user = MagicMock(id=1, roles={"admin"})
    return ctx


# =============================================================================
# File tools
# =============================================================================


@pytest.mark.asyncio
class TestFileTools:
    async def test_file_read_success(self, mock_ctx):
        mock_ctx.deps.storage.files.read = AsyncMock(return_value="file content")
        result = await file_read(mock_ctx, "test.txt")
        assert result == "file content"

    async def test_file_read_not_found(self, mock_ctx):
        mock_ctx.deps.storage.files.read = AsyncMock(side_effect=FileNotFoundError())
        result = await file_read(mock_ctx, "missing.txt")
        assert "not found" in result.lower()

    async def test_file_read_permission_denied(self, mock_ctx):
        mock_ctx.deps.storage.files.read = AsyncMock(side_effect=PermissionError())
        result = await file_read(mock_ctx, "secret.txt")
        assert "permission denied" in result.lower()

    async def test_file_write_success(self, mock_ctx):
        mock_ctx.deps.storage.files.write = AsyncMock()
        result = await file_write(mock_ctx, "test.txt", "hello")
        assert "5 bytes" in result

    async def test_file_write_permission_denied(self, mock_ctx):
        mock_ctx.deps.storage.files.write = AsyncMock(side_effect=PermissionError())
        result = await file_write(mock_ctx, "test.txt", "hello")
        assert "permission denied" in result.lower()

    async def test_file_list_success(self, mock_ctx):
        mock_ctx.deps.storage.files.list = AsyncMock(return_value=["a.py", "b.py"])
        result = await file_list(mock_ctx, "*.py")
        assert "a.py" in result
        assert "b.py" in result

    async def test_file_list_empty(self, mock_ctx):
        mock_ctx.deps.storage.files.list = AsyncMock(return_value=[])
        result = await file_list(mock_ctx)
        assert "no files" in result.lower()

    async def test_file_list_truncated(self, mock_ctx):
        files = [f"file{i}.txt" for i in range(100)]
        mock_ctx.deps.storage.files.list = AsyncMock(return_value=files)
        result = await file_list(mock_ctx)
        assert "more files" in result

    async def test_file_search_success(self, mock_ctx):
        matches = [Match(path="test.py", line=10, text="def test():")]
        mock_ctx.deps.storage.files.search = AsyncMock(return_value=matches)
        result = await file_search(mock_ctx, r"def \w+")
        assert "test.py:10" in result

    async def test_file_search_no_matches(self, mock_ctx):
        mock_ctx.deps.storage.files.search = AsyncMock(return_value=[])
        result = await file_search(mock_ctx, "nonexistent")
        assert "no matches" in result.lower()


# =============================================================================
# Memory tools
# =============================================================================


@pytest.mark.asyncio
class TestMemoryTools:
    async def test_memory_set(self, mock_ctx):
        mock_ctx.deps.storage.memory.set = AsyncMock()
        result = await memory_set(mock_ctx, "key", "value")
        assert "stored" in result.lower()

    async def test_memory_get_found(self, mock_ctx):
        mock_ctx.deps.storage.memory.get = AsyncMock(return_value="value")
        result = await memory_get(mock_ctx, "key")
        assert result == "value"

    async def test_memory_get_not_found(self, mock_ctx):
        mock_ctx.deps.storage.memory.get = AsyncMock(return_value=None)
        result = await memory_get(mock_ctx, "missing")
        assert "not found" in result.lower()

    async def test_memory_delete(self, mock_ctx):
        mock_ctx.deps.storage.memory.delete = AsyncMock()
        result = await memory_delete(mock_ctx, "key")
        assert "deleted" in result.lower()

    async def test_memory_list(self, mock_ctx):
        mock_ctx.deps.storage.memory.keys = AsyncMock(return_value=["key1", "key2"])
        result = await memory_list(mock_ctx)
        assert "key1" in result
        assert "key2" in result

    async def test_memory_list_empty(self, mock_ctx):
        mock_ctx.deps.storage.memory.keys = AsyncMock(return_value=[])
        result = await memory_list(mock_ctx)
        assert "no memories" in result.lower()


# =============================================================================
# Shell tools
# =============================================================================


@pytest.mark.asyncio
class TestShellTools:
    async def test_shell_exec_success(self, mock_ctx):
        mock_ctx.deps.workspace.shell.exec = AsyncMock(return_value=Result(code=0, stdout="output", stderr=""))
        result = await shell_exec(mock_ctx, "ls")
        assert "output" in result

    async def test_shell_exec_with_stderr(self, mock_ctx):
        mock_ctx.deps.workspace.shell.exec = AsyncMock(return_value=Result(code=0, stdout="", stderr="warning"))
        result = await shell_exec(mock_ctx, "cmd")
        assert "stderr" in result.lower()
        assert "warning" in result

    async def test_shell_exec_failure(self, mock_ctx):
        mock_ctx.deps.workspace.shell.exec = AsyncMock(return_value=Result(code=1, stdout="", stderr="error"))
        result = await shell_exec(mock_ctx, "bad")
        assert "exit code: 1" in result


# =============================================================================
# Project tools
# =============================================================================


@pytest.mark.asyncio
class TestProjectTools:
    async def test_project_current_selected(self, mock_ctx):
        mock_ctx.deps.workspace.projects.current = AsyncMock(return_value=("myproject", Path("/path")))
        result = await project_current(mock_ctx)
        assert "myproject" in result
        assert "/path" in result

    async def test_project_current_none(self, mock_ctx):
        mock_ctx.deps.workspace.projects.current = AsyncMock(return_value=None)
        result = await project_current(mock_ctx)
        assert "no project" in result.lower()

    async def test_project_list_success(self, mock_ctx):
        mock_ctx.deps.workspace.projects.list = AsyncMock(return_value=["proj1", "proj2"])
        mock_ctx.deps.workspace.projects.current = AsyncMock(return_value=("proj1", Path("/")))
        result = await project_list(mock_ctx)
        assert "proj1" in result
        assert "proj2" in result

    async def test_project_list_empty(self, mock_ctx):
        mock_ctx.deps.workspace.projects.list = AsyncMock(return_value=[])
        result = await project_list(mock_ctx)
        assert "no projects" in result.lower()

    async def test_project_switch_success(self, mock_ctx):
        mock_ctx.deps.switch_project = AsyncMock()
        result = await project_switch(mock_ctx, "newproj")
        assert "switched" in result.lower()

    async def test_project_switch_not_found(self, mock_ctx):
        mock_ctx.deps.switch_project = AsyncMock(side_effect=KeyError())
        result = await project_switch(mock_ctx, "missing")
        assert "not found" in result.lower()

    async def test_project_register_success(self, mock_ctx, tmp_path):
        mock_ctx.deps.workspace.projects.register = AsyncMock()
        result = await project_register(mock_ctx, "newproj", str(tmp_path))
        assert "registered" in result.lower()

    async def test_project_register_path_not_exists(self, mock_ctx):
        result = await project_register(mock_ctx, "proj", "/nonexistent/path")
        assert "not exist" in result.lower()


# =============================================================================
# Cron tools
# =============================================================================


@pytest.mark.asyncio
class TestCronTools:
    async def test_cron_create(self, mock_ctx):
        job = CronJob(id="job-1", schedule="* * * * *", task="test")
        mock_ctx.deps.scheduling.cron.create = AsyncMock(return_value=job)
        result = await cron_create(mock_ctx, "* * * * *", "test")
        assert "job-1" in result

    async def test_cron_get_found(self, mock_ctx):
        job = CronJob(id="job-1", schedule="* * * * *", task="test", enabled=True)
        mock_ctx.deps.scheduling.cron.get = AsyncMock(return_value=job)
        result = await cron_get(mock_ctx, "job-1")
        assert "job-1" in result
        assert "enabled" in result

    async def test_cron_get_not_found(self, mock_ctx):
        mock_ctx.deps.scheduling.cron.get = AsyncMock(return_value=None)
        result = await cron_get(mock_ctx, "missing")
        assert "not found" in result.lower()

    async def test_cron_list_success(self, mock_ctx):
        jobs = [CronJob(id="job-1", schedule="* * * * *", task="test", enabled=True)]
        mock_ctx.deps.scheduling.cron.list = AsyncMock(return_value=jobs)
        result = await cron_list(mock_ctx)
        assert "job-1" in result

    async def test_cron_list_empty(self, mock_ctx):
        mock_ctx.deps.scheduling.cron.list = AsyncMock(return_value=[])
        result = await cron_list(mock_ctx)
        assert "no scheduled" in result.lower()

    async def test_cron_enable(self, mock_ctx):
        mock_ctx.deps.scheduling.cron.enable = AsyncMock(return_value=True)
        result = await cron_enable(mock_ctx, "job-1")
        assert "enabled" in result.lower()

    async def test_cron_disable(self, mock_ctx):
        mock_ctx.deps.scheduling.cron.disable = AsyncMock(return_value=True)
        result = await cron_disable(mock_ctx, "job-1")
        assert "disabled" in result.lower()

    async def test_cron_delete(self, mock_ctx):
        mock_ctx.deps.scheduling.cron.delete = AsyncMock(return_value=True)
        result = await cron_delete(mock_ctx, "job-1")
        assert "deleted" in result.lower()

    async def test_cron_delete_not_found(self, mock_ctx):
        mock_ctx.deps.scheduling.cron.delete = AsyncMock(return_value=False)
        result = await cron_delete(mock_ctx, "missing")
        assert "not found" in result.lower()
