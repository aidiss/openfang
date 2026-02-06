"""Tests for subagent models."""

import pytest

from openfang.subagents.models import SubagentResult, SubagentRunRecord, SubagentSpec


class TestSubagentSpec:
    """Tests for SubagentSpec model."""

    def test_minimal_spec(self):
        """Test creating a spec with minimal fields."""
        spec = SubagentSpec(
            id="test",
            name="Test Agent",
            description="A test agent",
            system_prompt="You are a test agent.",
        )
        assert spec.id == "test"
        assert spec.name == "Test Agent"
        assert spec.model is None
        assert spec.tools is None
        assert spec.denied_tools == []
        assert spec.max_requests == 10

    def test_full_spec(self):
        """Test creating a spec with all fields."""
        spec = SubagentSpec(
            id="analyzer",
            name="Code Analyzer",
            description="Analyzes code",
            system_prompt="Analyze code carefully.",
            model="openai:gpt-4o",
            tools=["file_read", "file_search"],
            denied_tools=["shell_exec"],
            max_requests=20,
        )
        assert spec.id == "analyzer"
        assert spec.model == "openai:gpt-4o"
        assert spec.tools == ["file_read", "file_search"]
        assert spec.denied_tools == ["shell_exec"]
        assert spec.max_requests == 20

    def test_spec_validation_required_fields(self):
        """Test that required fields are enforced."""
        with pytest.raises(ValueError):
            SubagentSpec(id="test")  # type: ignore[call-arg] - Testing validation


class TestSubagentRunRecord:
    """Tests for SubagentRunRecord model."""

    def test_default_status(self):
        """Test that default status is pending."""
        record = SubagentRunRecord(
            run_id="run-1",
            subagent_id="test",
            task="Do something",
        )
        assert record.status == "pending"
        assert record.result is None
        assert record.error is None

    def test_status_transitions(self):
        """Test valid status values."""
        for status in ["pending", "running", "completed", "failed", "timeout"]:
            record = SubagentRunRecord(
                run_id="run-1",
                subagent_id="test",
                task="Do something",
                status=status,  # type: ignore[arg-type] - iterating over valid literals
            )
            assert record.status == status


class TestSubagentResult:
    """Tests for SubagentResult model."""

    def test_success_result(self):
        """Test a successful result."""
        result = SubagentResult(
            run_id="run-1",
            status="success",
            output="Task completed successfully",
            usage={"requests": 3, "total_tokens": 1500},
        )
        assert result.status == "success"
        assert result.output == "Task completed successfully"
        assert result.error is None

    def test_error_result(self):
        """Test an error result."""
        result = SubagentResult(
            run_id="run-1",
            status="error",
            error="Something went wrong",
        )
        assert result.status == "error"
        assert result.output is None
        assert result.error == "Something went wrong"

    def test_timeout_result(self):
        """Test a timeout result."""
        result = SubagentResult(
            run_id="run-1",
            status="timeout",
            error="Timed out after 300s",
        )
        assert result.status == "timeout"
