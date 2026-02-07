"""Session routes."""

from __future__ import annotations

from fastapi import APIRouter, Request, Response
from pydantic_ai.messages import ModelRequest, ModelResponse, TextPart, UserPromptPart

from openfang.chat import start_session
from openfang.gateway.deps import DepsDep, SessionsDataDep, get_sessions_data, templates
from openfang.gateway.helpers import htmx_or_json, is_htmx
from openfang.models import session_id_default, session_id_new

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
        session_id = session_id_new()

    await start_session(deps, session_id)

    if is_htmx(request):
        sessions = await get_sessions_data(deps)
        response = templates.TemplateResponse(
            request, "partials/sessions.html", {"sessions": sessions, "current_id": session_id}
        )
        response.set_cookie("session_id", session_id, httponly=True, samesite="lax")
        return response

    response = Response(content=f'{{"id": "{session_id}"}}', media_type="application/json")
    response.set_cookie("session_id", session_id, httponly=True, samesite="lax")
    return response


@router.post("/sessions/{session_id}/switch")
async def session_switch(request: Request, session_id: str, deps: DepsDep):
    """Switch to a session."""
    await start_session(deps, session_id)

    if is_htmx(request):
        sessions = await get_sessions_data(deps)
        response = templates.TemplateResponse(
            request, "partials/sessions.html", {"sessions": sessions, "current_id": session_id}
        )
        response.set_cookie("session_id", session_id, httponly=True, samesite="lax")
        return response

    response = Response(content=f'{{"switched_to": "{session_id}"}}', media_type="application/json")
    response.set_cookie("session_id", session_id, httponly=True, samesite="lax")
    return response


def _extract_message_content(msg) -> dict | None:
    """Extract role and content from a ModelMessage."""
    if isinstance(msg, ModelRequest):
        for part in msg.parts:
            if isinstance(part, UserPromptPart):
                content = part.content
                if isinstance(content, str):
                    return {"role": "user", "content": content}
                # For multimodal content, just use first text part
                for item in content:
                    if isinstance(item, str):
                        return {"role": "user", "content": item}
    elif isinstance(msg, ModelResponse):
        for part in msg.parts:
            if isinstance(part, TextPart):
                return {"role": "assistant", "content": part.content}
    return None


@router.get("/sessions/{session_id}/messages")
async def session_messages(request: Request, session_id: str, deps: DepsDep):
    """Get messages for a session."""
    raw_msgs = await deps.storage.sessions.get(session_id)
    messages = [m for msg in raw_msgs if (m := _extract_message_content(msg)) is not None]
    data = {"session_id": session_id, "messages": messages}
    return htmx_or_json(request, templates, "partials/session_messages.html", data)


@router.delete("/sessions/{session_id}")
async def session_delete(request: Request, session_id: str, deps: DepsDep):
    """Delete a session."""
    await deps.storage.sessions.delete(session_id)

    # If deleted current, switch to default
    if deps.session_id == session_id:
        await start_session(deps, session_id_default())

    if is_htmx(request):
        sessions = await get_sessions_data(deps)
        return templates.TemplateResponse(
            request, "partials/sessions.html", {"sessions": sessions, "current_id": deps.session_id}
        )
    return {"deleted": session_id}
