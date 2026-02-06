"""Subagent registry - loads and manages subagent specs."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from .models import SubagentSpec

if TYPE_CHECKING:
    from collections.abc import Iterable

# Bundled specs directory (relative to this file)
BUNDLED_DIR = Path(__file__).parent / "bundled"


class SubagentRegistry:
    """Registry for specialized subagent definitions."""

    def __init__(self) -> None:
        self._specs: dict[str, SubagentSpec] = {}

    def register(self, spec: SubagentSpec) -> None:
        """Register a subagent spec."""
        self._specs[spec.id] = spec

    def get(self, subagent_id: str) -> SubagentSpec | None:
        """Get a subagent spec by ID."""
        return self._specs.get(subagent_id)

    def all(self) -> list[SubagentSpec]:
        """Return all registered subagent specs."""
        return list(self._specs.values())

    def list_for_prompt(self) -> str:
        """Format available subagents for inclusion in agent instructions."""
        if not self._specs:
            return ""

        lines = ["## Available Subagents", ""]
        for spec in self._specs.values():
            lines.append(f"- **{spec.id}**: {spec.description}")
        lines.append("")
        lines.append("Use `subagent_delegate` to delegate tasks to these specialists.")
        return "\n".join(lines)

    def load_from_yaml(self, path: Path) -> SubagentSpec:
        """Load a single subagent spec from a YAML file."""
        with path.open() as f:
            data = yaml.safe_load(f)
        spec = SubagentSpec.model_validate(data)
        self.register(spec)
        return spec

    def load_directory(self, directory: Path) -> list[SubagentSpec]:
        """Load all subagent specs from YAML files in a directory."""
        specs = []
        if not directory.exists():
            return specs
        for path in directory.glob("*.yaml"):
            spec = self.load_from_yaml(path)
            specs.append(spec)
        for path in directory.glob("*.yml"):
            spec = self.load_from_yaml(path)
            specs.append(spec)
        return specs

    def load_bundled(self) -> list[SubagentSpec]:
        """Load bundled subagent specs."""
        return self.load_directory(BUNDLED_DIR)

    @classmethod
    def default(cls) -> SubagentRegistry:
        """Create a registry with bundled subagents loaded."""
        registry = cls()
        registry.load_bundled()
        return registry

    @classmethod
    def from_specs(cls, specs: Iterable[SubagentSpec]) -> SubagentRegistry:
        """Create a registry from a list of specs."""
        registry = cls()
        for spec in specs:
            registry.register(spec)
        return registry
