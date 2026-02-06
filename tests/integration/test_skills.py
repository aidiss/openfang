"""Integration tests for skill loading."""

import pytest

from openfang.skills.loader import load_skill, load_skills_from_dir, parse_frontmatter
from openfang.skills.registry import SkillRegistry


class TestSkillParsing:
    """Test SKILL.md parsing."""

    def test_parse_frontmatter_valid(self):
        content = """---
name: test-skill
description: A test skill
---

# Skill Content

This is the body.
"""
        frontmatter, body = parse_frontmatter(content)
        assert frontmatter["name"] == "test-skill"
        assert frontmatter["description"] == "A test skill"
        assert "# Skill Content" in body

    def test_parse_frontmatter_no_frontmatter(self):
        content = "# Just markdown\n\nNo frontmatter here."
        frontmatter, body = parse_frontmatter(content)
        assert frontmatter == {}
        assert body == content

    def test_parse_frontmatter_invalid_yaml(self):
        content = """---
invalid: yaml: syntax:
---

body
"""
        frontmatter, body = parse_frontmatter(content)
        assert frontmatter == {}


class TestSkillLoading:
    """Test loading skills from directories."""

    def test_load_skill_basic(self, tmp_path):
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: Does something useful
---

# Instructions

Use this skill to do things.
""")
        skill = load_skill(skill_dir, source="test")

        assert skill is not None
        assert skill.name == "my-skill"
        assert skill.description == "Does something useful"
        assert "# Instructions" in skill.content
        assert skill.source == "test"

    def test_load_skill_fallback_name(self, tmp_path):
        skill_dir = tmp_path / "fallback-name"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
description: No name specified
---

Content here.
""")
        skill = load_skill(skill_dir)

        assert skill is not None
        assert skill.name == "fallback-name"

    def test_load_skill_missing_file(self, tmp_path):
        skill_dir = tmp_path / "empty"
        skill_dir.mkdir()

        skill = load_skill(skill_dir)
        assert skill is None

    def test_load_skill_with_metadata(self, tmp_path):
        skill_dir = tmp_path / "meta-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: meta-skill
metadata:
  openfang:
    requires:
      bins: [python]
      env: [API_KEY]
---

Content.
""")
        skill = load_skill(skill_dir)

        assert skill is not None
        assert skill.metadata.requires is not None
        assert "python" in skill.metadata.requires.bins
        assert "API_KEY" in skill.metadata.requires.env

    def test_load_skills_from_dir(self, tmp_path):
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        # Create multiple skills
        for name in ["skill-a", "skill-b", "skill-c"]:
            d = skills_dir / name
            d.mkdir()
            (d / "SKILL.md").write_text(f"""---
name: {name}
description: {name} description
---

Content for {name}.
""")

        # Also create a non-skill directory
        (skills_dir / "not-a-skill").mkdir()

        skills = load_skills_from_dir(skills_dir, source="test-dir")

        assert len(skills) == 3
        assert "skill-a" in skills
        assert "skill-b" in skills
        assert "skill-c" in skills
        assert skills["skill-a"].source == "test-dir"

    def test_load_skills_from_nonexistent_dir(self, tmp_path):
        skills = load_skills_from_dir(tmp_path / "nonexistent")
        assert skills == {}


@pytest.mark.asyncio
class TestSkillRegistry:
    """Test skill registry operations."""

    async def test_registry_load_and_get(self, tmp_path):
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        skill_dir = skills_dir / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: test-skill
description: A test
user-invocable: true
---

Do the thing.
""")

        registry = SkillRegistry()
        registry.load_from_dir(skills_dir)

        skill = registry.get("test-skill")
        assert skill is not None
        assert skill.name == "test-skill"

    async def test_registry_invocable_skills(self, tmp_path):
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        # User-invocable skill
        s1 = skills_dir / "invocable"
        s1.mkdir()
        (s1 / "SKILL.md").write_text("""---
name: invocable
user-invocable: true
---
Content.
""")

        # Non-user-invocable skill
        s2 = skills_dir / "hidden"
        s2.mkdir()
        (s2 / "SKILL.md").write_text("""---
name: hidden
user-invocable: false
---
Content.
""")

        registry = SkillRegistry()
        registry.load_from_dir(skills_dir)

        user_skills = registry.invocable_skills()
        assert len(user_skills) == 1
        assert user_skills[0].name == "invocable"

    async def test_registry_format_for_prompt(self, tmp_path):
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        skill_dir = skills_dir / "commit"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: commit
description: Create a git commit
user-invocable: true
---

Instructions here.
""")

        registry = SkillRegistry()
        registry.load_from_dir(skills_dir)

        prompt = registry.format_for_prompt()
        assert "commit" in prompt
        assert "Create a git commit" in prompt
