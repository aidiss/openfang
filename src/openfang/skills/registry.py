"""Skill registry and eligibility checking."""

from __future__ import annotations

import logging
import os
import shutil
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from .loader import load_skills_from_dir

if TYPE_CHECKING:
    from .models import Skill

logger = logging.getLogger(__name__)

# Default bundled skills directory
BUNDLED_SKILLS_DIR = Path(__file__).parent / "bundled"


class SkillRegistry:
    """Registry for managing skills with eligibility checking."""

    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}
        self._eligible_cache: dict[str, bool] = {}

    @classmethod
    def default(cls) -> SkillRegistry:
        """Create registry with bundled skills loaded."""
        registry = cls()
        registry.load_bundled()
        return registry

    @property
    def skills(self) -> dict[str, Skill]:
        """All registered skills."""
        return self._skills

    def register(self, skill: Skill, override: bool = True) -> None:
        """Register a skill.

        Args:
            skill: Skill to register
            override: If True, override existing skill with same name
        """
        if skill.name in self._skills and not override:
            return
        self._skills[skill.name] = skill
        self._eligible_cache.pop(skill.name, None)

    def load_bundled(self) -> None:
        """Load bundled skills from the package."""
        skills = load_skills_from_dir(BUNDLED_SKILLS_DIR, source="bundled")
        for skill in skills.values():
            self.register(skill, override=False)

    def load_from_dir(self, path: Path, source: str = "custom") -> None:
        """Load skills from a directory.

        Later loads override earlier ones by name.
        """
        skills = load_skills_from_dir(path, source=source)
        for skill in skills.values():
            self.register(skill, override=True)

    def get(self, name: str) -> Skill | None:
        """Get a skill by name."""
        return self._skills.get(name)

    def is_eligible(self, skill: Skill) -> bool:
        """Check if a skill is eligible (requirements met)."""
        if skill.name in self._eligible_cache:
            return self._eligible_cache[skill.name]

        eligible = self._check_eligibility(skill)
        self._eligible_cache[skill.name] = eligible
        return eligible

    def _check_eligibility(self, skill: Skill) -> bool:
        """Check eligibility requirements for a skill."""
        meta = skill.metadata
        reqs = meta.requires

        # Always-included skills bypass checks
        if meta.always:
            return True

        # OS check
        if meta.os:
            current_os = "darwin" if sys.platform == "darwin" else "linux"
            if current_os not in meta.os:
                logger.debug(f"Skill {skill.name}: OS {current_os} not in {meta.os}")
                return False

        # Required binaries (all must exist)
        for bin_name in reqs.bins:
            if not shutil.which(bin_name):
                logger.debug(f"Skill {skill.name}: missing binary {bin_name}")
                return False

        # Any binaries (at least one must exist)
        if reqs.any_bins and not any(shutil.which(b) for b in reqs.any_bins):
            logger.debug(f"Skill {skill.name}: no binary in {reqs.any_bins}")
            return False

        # Environment variables
        for env_var in reqs.env:
            if not os.environ.get(env_var):
                logger.debug(f"Skill {skill.name}: missing env var {env_var}")
                return False

        return True

    def eligible_skills(self) -> list[Skill]:
        """Get all eligible skills."""
        return [s for s in self._skills.values() if self.is_eligible(s)]

    def invocable_skills(self) -> list[Skill]:
        """Get skills that can be invoked by users."""
        return [s for s in self.eligible_skills() if s.user_invocable]

    def model_skills(self) -> list[Skill]:
        """Get skills available to the model."""
        return [s for s in self.eligible_skills() if not s.disable_model_invocation]

    def format_for_prompt(self, skills: list[Skill] | None = None) -> str:
        """Format skills for inclusion in agent prompt.

        Args:
            skills: Skills to include, defaults to model_skills()
        """
        if skills is None:
            skills = self.model_skills()

        if not skills:
            return ""

        parts = ["# Available Skills\n"]
        for skill in skills:
            parts.append(skill.format_for_prompt())
            parts.append("")

        return "\n".join(parts)


# Default registry instance
default_registry = SkillRegistry()
