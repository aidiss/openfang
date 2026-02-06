"""Skill data models."""

from __future__ import annotations

from pathlib import Path  # noqa: TC003 - used at runtime in methods
from typing import Literal

from pydantic import BaseModel, Field


class SkillRequirements(BaseModel):
    """Requirements that must be met for a skill to be available."""

    bins: list[str] = Field(default_factory=list)
    """Binaries that must all be available."""

    any_bins: list[str] = Field(default_factory=list, alias="anyBins")
    """At least one of these binaries must be available."""

    env: list[str] = Field(default_factory=list)
    """Environment variables that must be set."""

    config: list[str] = Field(default_factory=list)
    """Config paths that must be truthy."""


class InstallSpec(BaseModel):
    """Installation specification for a dependency."""

    id: str
    kind: Literal["brew", "apt", "pip", "uv", "node", "download"]
    label: str | None = None

    # Kind-specific fields
    formula: str | None = None  # brew
    package: str | None = None  # apt, pip, uv, node
    url: str | None = None  # download
    bins: list[str] = Field(default_factory=list)


class SkillMetadata(BaseModel):
    """OpenFang-specific skill metadata."""

    emoji: str | None = None
    requires: SkillRequirements = Field(default_factory=SkillRequirements)
    primary_env: str | None = Field(default=None, alias="primaryEnv")
    install: list[InstallSpec] = Field(default_factory=list)
    os: list[str] | None = None
    always: bool = False

    model_config = {"populate_by_name": True}


class Skill(BaseModel):
    """A loaded skill."""

    name: str
    description: str
    content: str
    """The markdown body (instructions)."""

    base_dir: Path
    """Directory containing the skill."""

    source: str = "unknown"
    """Where the skill was loaded from (bundled, workspace, etc)."""

    homepage: str | None = None
    user_invocable: bool = True
    disable_model_invocation: bool = False

    metadata: SkillMetadata = Field(default_factory=SkillMetadata)

    model_config = {"arbitrary_types_allowed": True}

    @property
    def references_dir(self) -> Path | None:
        """Path to bundled references, if any."""
        refs = self.base_dir / "references"
        return refs if refs.is_dir() else None

    @property
    def scripts_dir(self) -> Path | None:
        """Path to bundled scripts, if any."""
        scripts = self.base_dir / "scripts"
        return scripts if scripts.is_dir() else None

    def get_reference(self, name: str) -> str | None:
        """Load a bundled reference file."""
        if not self.references_dir:
            return None
        ref_path = self.references_dir / name
        if ref_path.is_file():
            return ref_path.read_text()
        return None

    def format_for_prompt(self) -> str:
        """Format skill for inclusion in agent prompt."""
        parts = [f"## Skill: {self.name}"]
        if self.metadata.emoji:
            parts[0] = f"## {self.metadata.emoji} Skill: {self.name}"
        if self.description:
            parts.append(f"\n{self.description}")
        if self.content:
            parts.append(f"\n{self.content}")
        return "\n".join(parts)
