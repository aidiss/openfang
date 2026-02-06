"""Tests for subagent tools."""

from dataclasses import dataclass, field
from unittest.mock import AsyncMock, MagicMock

import pytest

from openfang.subagents.models import SubagentResult, SubagentSpec
from openfang.subagents.registry import SubagentRegistry
from openfang.subagents.tools import subagent_delegate, subagent_list


@dataclass
class FakeSubagentExecutor:
    """Fake executor for testing."""

    calls: list[tuple[str, str]] = field(default_factory=list)
    result: SubagentResult | None = None

    async def run_sync(self, spec, task, deps, timeout_seconds=300):
        self.calls.append((spec.id, task))
        if self.result:
            return self.result
        return SubagentResult(
            run_id="fake-run",
            status="success",
            output=f"Fake result for: {task}",
        )


@pytest.fixture
def test_specs():
    """Create test subagent specs."""
    return [
        SubagentSpec(
            id="code-analyzer",
            name="Code Analyzer",
            description="Analyzes code for issues",
            system_prompt="Analyze code.",
            tools=["file_read", "file_search"],
        ),
        SubagentSpec(
            id="summarizer",
            name="Summarizer",
            description="Summarizes text",
            system_prompt="Summarize.",
            tools=[],
        ),
    ]


@pytest.fixture
def registry(test_specs):
    """Create a registry with test specs."""
    return SubagentRegistry.from_specs(test_specs)


@pytest.fixture
def fake_executor():
    """Create a fake executor."""
    return FakeSubagentExecutor()


@pytest.fixture
def mock_ctx(registry, fake_executor):
    """Create a mock RunContext with deps."""
    ctx = MagicMock()
    ctx.deps.is_subagent = False
    ctx.deps.subagents = registry
    ctx.deps.subagent_executor = fake_executor
    return ctx


class TestSubagentList:
    """Tests for subagent_list tool."""

    @pytest.mark.asyncio
    async def test_list_subagents(self, mock_ctx):
        """Test listing available subagents."""
        result = await subagent_list(mock_ctx)

        assert "code-analyzer" in result
        assert "Analyzes code" in result
        assert "summarizer" in result
        assert "Summarizes text" in result

    @pytest.mark.asyncio
    async def test_list_no_subagents_configured(self, mock_ctx):
        """Test when subagents not configured."""
        mock_ctx.deps.subagents = None

        result = await subagent_list(mock_ctx)
        assert "No subagents configured" in result

    @pytest.mark.asyncio
    async def test_list_empty_registry(self, mock_ctx):
        """Test with empty registry."""
        mock_ctx.deps.subagents = SubagentRegistry()

        result = await subagent_list(mock_ctx)
        assert "No subagents available" in result


class TestSubagentDelegate:
    """Tests for subagent_delegate tool."""

    @pytest.mark.asyncio
    async def test_delegate_success(self, mock_ctx, fake_executor):
        """Test successful delegation."""
        result = await subagent_delegate(
            mock_ctx,
            subagent_id="code-analyzer",
            task="Analyze this code",
        )

        assert "[Code Analyzer]" in result
        assert "Fake result for: Analyze this code" in result
        assert len(fake_executor.calls) == 1
        assert fake_executor.calls[0] == ("code-analyzer", "Analyze this code")

    @pytest.mark.asyncio
    async def test_delegate_unknown_subagent(self, mock_ctx):
        """Test delegation to unknown subagent."""
        result = await subagent_delegate(
            mock_ctx,
            subagent_id="nonexistent",
            task="Do something",
        )

        assert "Error" in result
        assert "Unknown subagent" in result
        assert "code-analyzer" in result  # Lists available

    @pytest.mark.asyncio
    async def test_delegate_prevents_recursion(self, mock_ctx):
        """Test that subagents cannot delegate."""
        mock_ctx.deps.is_subagent = True

        result = await subagent_delegate(
            mock_ctx,
            subagent_id="code-analyzer",
            task="Try to recurse",
        )

        assert "Error" in result
        assert "cannot delegate" in result

    @pytest.mark.asyncio
    async def test_delegate_no_subagent_system(self, mock_ctx):
        """Test when subagent system not configured."""
        mock_ctx.deps.subagents = None
        mock_ctx.deps.subagent_executor = None

        result = await subagent_delegate(
            mock_ctx,
            subagent_id="code-analyzer",
            task="Do something",
        )

        assert "Error" in result
        assert "not configured" in result

    @pytest.mark.asyncio
    async def test_delegate_timeout(self, mock_ctx, fake_executor):
        """Test delegation timeout."""
        fake_executor.result = SubagentResult(
            run_id="timeout-run",
            status="timeout",
            error="Timed out after 60s",
        )

        result = await subagent_delegate(
            mock_ctx,
            subagent_id="code-analyzer",
            task="Long task",
            timeout_seconds=60,
        )

        assert "Error" in result
        assert "timed out" in result

    @pytest.mark.asyncio
    async def test_delegate_error(self, mock_ctx, fake_executor):
        """Test delegation error."""
        fake_executor.result = SubagentResult(
            run_id="error-run",
            status="error",
            error="Something went wrong",
        )

        result = await subagent_delegate(
            mock_ctx,
            subagent_id="code-analyzer",
            task="Fail task",
        )

        assert "Error" in result
        assert "failed" in result
        assert "Something went wrong" in result
