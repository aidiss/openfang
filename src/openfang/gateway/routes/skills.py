"""Skills routes."""

from __future__ import annotations

from fastapi import APIRouter, Request

from openfang.gateway.deps import DepsDep, templates
from openfang.gateway.helpers import htmx_or_json

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("")
async def skills_list(request: Request, deps: DepsDep):
    """List available skills."""
    all_skills = list(deps.comms.skills.skills.values())
    eligible = deps.comms.skills.eligible_skills()
    eligible_names = {s.name for s in eligible}

    skill_data = [
        {
            "name": skill.name,
            "description": skill.description,
            "emoji": skill.metadata.emoji,
            "eligible": skill.name in eligible_names,
            "user_invocable": skill.user_invocable,
            "requires_env": skill.metadata.requires.env,
            "requires_bins": skill.metadata.requires.bins,
        }
        for skill in all_skills
    ]
    return htmx_or_json(request, templates, "partials/skills.html", {"skills": skill_data})
