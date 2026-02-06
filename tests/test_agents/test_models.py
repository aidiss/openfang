"""Tests for agent models."""

import pytest

from openfang.agents.models import AgentConfig, AgentIdentity, AgentToolPolicy


class TestAgentIdentity:
    """Tests for AgentIdentity model."""

    def test_defaults(self):
        """Test default values."""
        identity = AgentIdentity()
        assert identity.name == "Assistant"
        assert identity.emoji == "🤖"

    def test_custom_values(self):
        """Test custom values."""
        identity = AgentIdentity(name="Cody", emoji="🦊")
        assert identity.name == "Cody"
        assert identity.emoji == "🦊"


class TestAgentToolPolicy:
    """Tests for AgentToolPolicy model."""

    def test_defaults(self):
        """Test default values."""
        policy = AgentToolPolicy()
        assert policy.allow is None
        assert policy.deny == []

    def test_allow_list(self):
        """Test with allowlist."""
        policy = AgentToolPolicy(allow=["file_read", "file_list"])
        assert policy.allow == ["file_read", "file_list"]

    def test_deny_list(self):
        """Test with denylist."""
        policy = AgentToolPolicy(deny=["shell_exec", "file_write"])
        assert policy.deny == ["shell_exec", "file_write"]


class TestAgentConfig:
    """Tests for AgentConfig model."""

    def test_minimal_config(self):
        """Test creating config with minimal fields."""
        config = AgentConfig(id="test", name="Test Agent")
        assert config.id == "test"
        assert config.name == "Test Agent"
        assert config.default is False
        assert config.model is None
        assert config.system_prompt is None
        assert config.identity.name == "Assistant"
        assert config.tools.allow is None
        assert config.skills is None
        assert config.subagent_allow == ["*"]

    def test_full_config(self):
        """Test creating config with all fields."""
        config = AgentConfig(
            id="coder",
            name="Coding Assistant",
            default=True,
            model="anthropic:claude-sonnet",
            system_prompt="You are a coding expert.",
            identity=AgentIdentity(name="Cody", emoji="💻"),
            tools=AgentToolPolicy(allow=["file_read", "file_write"], deny=["shell_exec"]),
            skills=["python", "javascript"],
            subagent_allow=["code-analyzer"],
        )
        assert config.id == "coder"
        assert config.default is True
        assert config.model == "anthropic:claude-sonnet"
        assert config.identity.name == "Cody"
        assert config.skills == ["python", "javascript"]
        assert config.subagent_allow == ["code-analyzer"]

    def test_can_use_tool_no_restrictions(self):
        """Test can_use_tool with no restrictions."""
        config = AgentConfig(id="test", name="Test")
        assert config.can_use_tool("file_read") is True
        assert config.can_use_tool("shell_exec") is True
        assert config.can_use_tool("anything") is True

    def test_can_use_tool_with_allowlist(self):
        """Test can_use_tool with allowlist."""
        config = AgentConfig(
            id="test",
            name="Test",
            tools=AgentToolPolicy(allow=["file_read", "file_list"]),
        )
        assert config.can_use_tool("file_read") is True
        assert config.can_use_tool("file_list") is True
        assert config.can_use_tool("shell_exec") is False
        assert config.can_use_tool("file_write") is False

    def test_can_use_tool_with_denylist(self):
        """Test can_use_tool with denylist."""
        config = AgentConfig(
            id="test",
            name="Test",
            tools=AgentToolPolicy(deny=["shell_exec", "file_write"]),
        )
        assert config.can_use_tool("file_read") is True
        assert config.can_use_tool("file_list") is True
        assert config.can_use_tool("shell_exec") is False
        assert config.can_use_tool("file_write") is False

    def test_can_use_tool_deny_overrides_allow(self):
        """Test that deny takes precedence over allow."""
        config = AgentConfig(
            id="test",
            name="Test",
            tools=AgentToolPolicy(
                allow=["file_read", "file_write", "shell_exec"],
                deny=["shell_exec"],
            ),
        )
        assert config.can_use_tool("file_read") is True
        assert config.can_use_tool("file_write") is True
        assert config.can_use_tool("shell_exec") is False

    def test_can_spawn_subagent_wildcard(self):
        """Test can_spawn_subagent with wildcard."""
        config = AgentConfig(id="test", name="Test", subagent_allow=["*"])
        assert config.can_spawn_subagent("code-analyzer") is True
        assert config.can_spawn_subagent("web-researcher") is True
        assert config.can_spawn_subagent("anything") is True

    def test_can_spawn_subagent_specific(self):
        """Test can_spawn_subagent with specific list."""
        config = AgentConfig(
            id="test",
            name="Test",
            subagent_allow=["code-analyzer", "summarizer"],
        )
        assert config.can_spawn_subagent("code-analyzer") is True
        assert config.can_spawn_subagent("summarizer") is True
        assert config.can_spawn_subagent("web-researcher") is False

    def test_can_spawn_subagent_empty(self):
        """Test can_spawn_subagent with empty list."""
        config = AgentConfig(id="test", name="Test", subagent_allow=[])
        assert config.can_spawn_subagent("code-analyzer") is False
        assert config.can_spawn_subagent("anything") is False
