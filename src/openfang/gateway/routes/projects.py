"""Projects routes."""

from __future__ import annotations

from fastapi import APIRouter, Request

from openfang.gateway.deps import DepsDep, templates
from openfang.gateway.helpers import htmx_or_json

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("")
async def projects_list(request: Request, deps: DepsDep):
    """List projects."""
    project_ids = await deps.workspace.projects.list()
    current = await deps.workspace.projects.current()
    data = {"projects": project_ids, "current": current}
    return htmx_or_json(request, templates, "partials/projects.html", data)
