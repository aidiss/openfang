"""Tests for subagent registry."""

from pathlib import Path
from tempfile import TemporaryDirectory


from openfang.subagents.models import SubagentSpec
from openfang.subagents.registry import SubagentRegistry


class TestSubagentRegistry:
    """Tests for SubagentRegistry."""

    def test_empty_registry(self):
        """Test empty registry."""
        registry = SubagentRegistry()
        assert registry.all() == []
        assert registry.get("nonexistent") is None

    def test_register_and_get(self):
        """Test registering and retrieving a spec."""
        registry = SubagentRegistry()
        spec = SubagentSpec(
            id="test",
            name="Test",
            description="Test agent",
            system_prompt="Test",
        )
        registry.register(spec)

        assert registry.get("test") == spec
        assert registry.get("nonexistent") is None
        assert len(registry.all()) == 1

    def test_register_overwrites(self):
        """Test that registering same ID overwrites."""
        registry = SubagentRegistry()
        spec1 = SubagentSpec(id="test", name="Test 1", description="First", system_prompt="1")
        spec2 = SubagentSpec(id="test", name="Test 2", description="Second", system_prompt="2")

        registry.register(spec1)
        registry.register(spec2)

        assert len(registry.all()) == 1
        spec = registry.get("test")
        assert spec is not None
        assert spec.name == "Test 2"

    def test_list_for_prompt_empty(self):
        """Test list_for_prompt with empty registry."""
        registry = SubagentRegistry()
        assert registry.list_for_prompt() == ""

    def test_list_for_prompt_with_specs(self):
        """Test list_for_prompt with specs."""
        registry = SubagentRegistry()
        registry.register(
            SubagentSpec(
                id="analyzer",
                name="Analyzer",
                description="Analyzes code",
                system_prompt="...",
            )
        )
        registry.register(
            SubagentSpec(
                id="researcher",
                name="Researcher",
                description="Researches topics",
                system_prompt="...",
            )
        )

        prompt = registry.list_for_prompt()
        assert "## Available Subagents" in prompt
        assert "analyzer" in prompt
        assert "Analyzes code" in prompt
        assert "researcher" in prompt
        assert "subagent_delegate" in prompt

    def test_load_from_yaml(self):
        """Test loading a spec from YAML."""
        with TemporaryDirectory() as tmpdir:
            yaml_content = """
id: test-agent
name: Test Agent
description: A test agent for testing
system_prompt: |
  You are a test agent.
  Be helpful.
tools:
  - file_read
  - file_list
max_requests: 15
"""
            yaml_path = Path(tmpdir) / "test.yaml"
            yaml_path.write_text(yaml_content)

            registry = SubagentRegistry()
            spec = registry.load_from_yaml(yaml_path)

            assert spec.id == "test-agent"
            assert spec.name == "Test Agent"
            assert spec.tools == ["file_read", "file_list"]
            assert spec.max_requests == 15
            assert registry.get("test-agent") == spec

    def test_load_directory(self):
        """Test loading specs from a directory."""
        with TemporaryDirectory() as tmpdir:
            # Create two YAML files
            (Path(tmpdir) / "agent1.yaml").write_text("""
id: agent1
name: Agent 1
description: First agent
system_prompt: You are agent 1.
""")
            (Path(tmpdir) / "agent2.yml").write_text("""
id: agent2
name: Agent 2
description: Second agent
system_prompt: You are agent 2.
""")
            # Non-yaml file should be ignored
            (Path(tmpdir) / "readme.txt").write_text("Not a spec")

            registry = SubagentRegistry()
            specs = registry.load_directory(Path(tmpdir))

            assert len(specs) == 2
            assert registry.get("agent1") is not None
            assert registry.get("agent2") is not None

    def test_load_directory_nonexistent(self):
        """Test loading from nonexistent directory."""
        registry = SubagentRegistry()
        specs = registry.load_directory(Path("/nonexistent/path"))
        assert specs == []

    def test_default_loads_bundled(self):
        """Test that default() loads bundled specs."""
        registry = SubagentRegistry.default()
        specs = registry.all()

        # Should have the bundled specs
        assert len(specs) >= 1
        ids = [s.id for s in specs]
        assert "code-analyzer" in ids or "web-researcher" in ids or "summarizer" in ids

    def test_from_specs(self):
        """Test creating registry from list of specs."""
        specs = [
            SubagentSpec(id="a", name="A", description="A", system_prompt="A"),
            SubagentSpec(id="b", name="B", description="B", system_prompt="B"),
        ]
        registry = SubagentRegistry.from_specs(specs)

        assert len(registry.all()) == 2
        assert registry.get("a") is not None
        assert registry.get("b") is not None
