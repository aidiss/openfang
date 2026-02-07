"""Session routes."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Request

from openfang.chat import start_session
from openfang.gateway.deps import DepsDep, SessionsDataDep, get_sessions_data, templates
from openfang.gateway.helpers import htmx_or_json, is_htmx

router = APIRouter(tags=["sessions"])


@router.get("/session/current")
async def current_session(request: Request, deps: DepsDep):
    """Get current session info."""
    session_id = deps.session_id
    msgs = await deps.storage.sessions.get(session_id) if session_id else []
    data = {"session_id": session_id, "message_count": len(msgs)}
    return htmx_or_json(request, templates, "partials/chat_header.html", data)


@router.get("/sessions")
async def sessions_list(request: Request, deps: DepsDep, sessions: SessionsDataDep):
    """List sessions."""
    data = {"sessions": sessions, "current_id": deps.session_id}
    return htmx_or_json(request, templates, "partials/sessions.html", data)


@router.post("/sessions")
async def session_create(request: Request, deps: DepsDep):
    """Create a new session."""
    form = await request.form()
    session_id = form.get("id", "").strip()

    if not session_id:
        session_id = f"session-{uuid.uuid4().hex[:8]}"

    await start_session(deps, session_id)

    if is_htmx(request):
        sessions = await get_sessions_data(deps)
        return templates.TemplateResponse(
            request, "partials/sessions.html", {"sessions": sessions, "current_id": session_id}
        )
    return {"id": session_id}


@router.post("/sessions/{session_id}/switch")
async def session_switch(request: Request, session_id: str, deps: DepsDep):
    """Switch to a session."""
    await start_session(deps, session_id)

    if is_htmx(request):
        sessions = await get_sessions_data(deps)
        return templates.TemplateResponse(
            request, "partials/sessions.html", {"sessions": sessions, "current_id": session_id}
        )
    return {"switched_to": session_id}


@router.delete("/sessions/{session_id}")
async def session_delete(request: Request, session_id: str, deps: DepsDep):
    """Delete a session."""
    await deps.storage.sessions.delete(session_id)

    # If deleted current, switch to a new one
    if deps.session_id == session_id:
        await start_session(deps, "web-session")

    if is_htmx(request):
        sessions = await get_sessions_data(deps)
        return templates.TemplateResponse(
            request, "partials/sessions.html", {"sessions": sessions, "current_id": deps.session_id}
        )
    return {"deleted": session_id}
