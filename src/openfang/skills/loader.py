"""Skill loading from SKILL.md files."""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Any

import yaml

from .models import Skill, SkillMetadata

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)

# Regex for YAML frontmatter
FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter from markdown content.

    Returns (frontmatter_dict, body_content).
    """
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        return {}, content

    try:
        frontmatter = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as e:
        logger.warning(f"Failed to parse YAML frontmatter: {e}")
        return {}, content

    body = content[match.end() :].strip()
    return frontmatter, body


def extract_openfang_metadata(frontmatter: dict[str, Any]) -> SkillMetadata:
    """Extract OpenFang metadata from frontmatter."""
    metadata_raw = frontmatter.get("metadata", {})

    # Try openfang key first, fall back to openclaw for compatibility
    openfang_meta = metadata_raw.get("openfang") or metadata_raw.get("openclaw") or {}

    return SkillMetadata.model_validate(openfang_meta)


def load_skill(skill_dir: Path, source: str = "unknown") -> Skill | None:
    """Load a skill from a directory containing SKILL.md.

    Args:
        skill_dir: Directory containing SKILL.md
        source: Where the skill was loaded from (for tracking)

    Returns:
        Skill object or None if loading failed
    """
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        return None

    try:
        content = skill_file.read_text()
        frontmatter, body = parse_frontmatter(content)

        name = frontmatter.get("name")
        if not name:
            # Fall back to directory name
            name = skill_dir.name

        description = frontmatter.get("description", "")
        homepage = frontmatter.get("homepage")
        user_invocable = frontmatter.get("user-invocable", True)
        disable_model = frontmatter.get("disable-model-invocation", False)

        metadata = extract_openfang_metadata(frontmatter)

        return Skill(
            name=name,
            description=description,
            content=body,
            base_dir=skill_dir,
            source=source,
            homepage=homepage,
            user_invocable=user_invocable,
            disable_model_invocation=disable_model,
            metadata=metadata,
        )

    except Exception as e:
        logger.warning(f"Failed to load skill from {skill_dir}: {e}")
        return None


def load_skills_from_dir(skills_dir: Path, source: str = "unknown") -> dict[str, Skill]:
    """Load all skills from a directory.

    Each subdirectory containing SKILL.md is treated as a skill.

    Args:
        skills_dir: Directory containing skill subdirectories
        source: Source identifier for loaded skills

    Returns:
        Dict mapping skill name to Skill object
    """
    skills: dict[str, Skill] = {}

    if not skills_dir.is_dir():
        return skills

    for item in skills_dir.iterdir():
        if not item.is_dir():
            continue

        skill = load_skill(item, source=source)
        if skill:
            skills[skill.name] = skill
            logger.debug(f"Loaded skill: {skill.name} from {source}")

    return skills
