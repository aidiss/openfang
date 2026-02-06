"""Conversation routes."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Request

from openfang.chat import start_conversation
from openfang.gateway.deps import ConversationsDataDep, DepsDep, get_conversations_data, templates
from openfang.gateway.helpers import htmx_or_json, is_htmx

router = APIRouter(tags=["conversations"])


@router.get("/conversation/current")
async def current_conversation(request: Request, deps: DepsDep):
    """Get current conversation info."""
    conv_id = deps.conversation_id
    msgs = await deps.storage.conversations.get(conv_id) if conv_id else []
    data = {"conversation_id": conv_id, "message_count": len(msgs)}
    return htmx_or_json(request, templates, "partials/chat_header.html", data)


@router.get("/conversations")
async def conversations_list(request: Request, deps: DepsDep, convs: ConversationsDataDep):
    """List conversations."""
    data = {"conversations": convs, "current_id": deps.conversation_id}
    return htmx_or_json(request, templates, "partials/conversations.html", data)


@router.post("/conversations")
async def conversation_create(request: Request, deps: DepsDep):
    """Create a new conversation."""
    form = await request.form()
    conv_id = form.get("id", "").strip()

    if not conv_id:
        conv_id = f"conv-{uuid.uuid4().hex[:8]}"

    await start_conversation(deps, conv_id)

    if is_htmx(request):
        convs = await get_conversations_data(deps)
        return templates.TemplateResponse(
            request, "partials/conversations.html", {"conversations": convs, "current_id": conv_id}
        )
    return {"id": conv_id}


@router.post("/conversations/{conv_id}/switch")
async def conversation_switch(request: Request, conv_id: str, deps: DepsDep):
    """Switch to a conversation."""
    await start_conversation(deps, conv_id)

    if is_htmx(request):
        convs = await get_conversations_data(deps)
        return templates.TemplateResponse(
            request, "partials/conversations.html", {"conversations": convs, "current_id": conv_id}
        )
    return {"switched_to": conv_id}


@router.delete("/conversations/{conv_id}")
async def conversation_delete(request: Request, conv_id: str, deps: DepsDep):
    """Delete a conversation."""
    await deps.storage.conversations.delete(conv_id)

    # If deleted current, switch to a new one
    if deps.conversation_id == conv_id:
        await start_conversation(deps, "web-session")

    if is_htmx(request):
        convs = await get_conversations_data(deps)
        return templates.TemplateResponse(
            request, "partials/conversations.html", {"conversations": convs, "current_id": deps.conversation_id}
        )
    return {"deleted": conv_id}
