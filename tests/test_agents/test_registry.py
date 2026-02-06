"""Tests for agent registry."""

from pathlib import Path
from tempfile import TemporaryDirectory


from openfang.agents.models import AgentConfig
from openfang.agents.registry import AgentRegistry


class TestAgentRegistry:
    """Tests for AgentRegistry."""

    def test_empty_registry(self):
        """Test empty registry."""
        registry = AgentRegistry()
        assert registry.all() == []
        assert registry.get("nonexistent") is None
        assert registry.get_default() is None

    def test_register_and_get(self):
        """Test registering and retrieving a config."""
        registry = AgentRegistry()
        config = AgentConfig(id="test", name="Test Agent")
        registry.register(config)

        assert registry.get("test") == config
        assert registry.get("nonexistent") is None
        assert len(registry.all()) == 1

    def test_register_default(self):
        """Test registering a default agent."""
        registry = AgentRegistry()
        config1 = AgentConfig(id="agent1", name="Agent 1", default=False)
        config2 = AgentConfig(id="agent2", name="Agent 2", default=True)
        config3 = AgentConfig(id="agent3", name="Agent 3", default=False)

        registry.register(config1)
        registry.register(config2)
        registry.register(config3)

        assert registry.get_default() == config2

    def test_get_default_fallback(self):
        """Test get_default falls back to first if no explicit default."""
        registry = AgentRegistry()
        config1 = AgentConfig(id="agent1", name="Agent 1")
        config2 = AgentConfig(id="agent2", name="Agent 2")

        registry.register(config1)
        registry.register(config2)

        default = registry.get_default()
        assert default is not None
        # Should return first registered
        assert default.id in ["agent1", "agent2"]

    def test_register_overwrites(self):
        """Test that registering same ID overwrites."""
        registry = AgentRegistry()
        config1 = AgentConfig(id="test", name="Test 1")
        config2 = AgentConfig(id="test", name="Test 2")

        registry.register(config1)
        registry.register(config2)

        assert len(registry.all()) == 1
        agent = registry.get("test")
        assert agent is not None
        assert agent.name == "Test 2"

    def test_load_from_yaml(self):
        """Test loading a config from YAML."""
        with TemporaryDirectory() as tmpdir:
            yaml_content = """
id: yaml-agent
name: YAML Agent
default: true
model: openai:gpt-4o
identity:
  name: Yammy
  emoji: "📄"
tools:
  allow:
    - file_read
    - file_list
  deny:
    - shell_exec
skills:
  - python
  - javascript
subagent_allow:
  - code-analyzer
"""
            yaml_path = Path(tmpdir) / "agent.yaml"
            yaml_path.write_text(yaml_content)

            registry = AgentRegistry()
            config = registry.load_from_yaml(yaml_path)

            assert config.id == "yaml-agent"
            assert config.name == "YAML Agent"
            assert config.default is True
            assert config.model == "openai:gpt-4o"
            assert config.identity.name == "Yammy"
            assert config.identity.emoji == "📄"
            assert config.tools.allow == ["file_read", "file_list"]
            assert config.tools.deny == ["shell_exec"]
            assert config.skills == ["python", "javascript"]
            assert config.subagent_allow == ["code-analyzer"]
            assert registry.get("yaml-agent") == config

    def test_load_directory(self):
        """Test loading configs from a directory."""
        with TemporaryDirectory() as tmpdir:
            # Create two YAML files
            (Path(tmpdir) / "agent1.yaml").write_text("""
id: agent1
name: Agent 1
default: true
""")
            (Path(tmpdir) / "agent2.yml").write_text("""
id: agent2
name: Agent 2
""")
            # Non-yaml file should be ignored
            (Path(tmpdir) / "readme.txt").write_text("Not a config")

            registry = AgentRegistry()
            configs = registry.load_directory(Path(tmpdir))

            assert len(configs) == 2
            assert registry.get("agent1") is not None
            assert registry.get("agent2") is not None
            default = registry.get_default()
            assert default is not None
            assert default.id == "agent1"

    def test_load_directory_nonexistent(self):
        """Test loading from nonexistent directory."""
        registry = AgentRegistry()
        configs = registry.load_directory(Path("/nonexistent/path"))
        assert configs == []

    def test_default_loads_bundled(self):
        """Test that default() loads bundled configs."""
        registry = AgentRegistry.default()
        configs = registry.all()

        # Should have at least the main bundled config
        assert len(configs) >= 1
        assert registry.get("main") is not None
        assert registry.get_default() is not None

    def test_from_configs(self):
        """Test creating registry from list of configs."""
        configs = [
            AgentConfig(id="a", name="A"),
            AgentConfig(id="b", name="B", default=True),
        ]
        registry = AgentRegistry.from_configs(configs)

        assert len(registry.all()) == 2
        assert registry.get("a") is not None
        assert registry.get("b") is not None
        default = registry.get_default()
        assert default is not None
        assert default.id == "b"
