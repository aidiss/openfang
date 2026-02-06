"""SSE events route."""

from __future__ import annotations

import json

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from openfang.gateway.deps import GatewayDep, templates

router = APIRouter(tags=["events"])


@router.get("/events")
async def events(request: Request, gateway: GatewayDep):
    """SSE event stream for real-time updates."""

    async def stream():
        async for event in gateway.events():
            event_type = event.get("type", "message")

            if event_type == "chat":
                content = event.get("content", "")
                role = event.get("role", "assistant")
                html = templates.TemplateResponse(
                    request, "partials/message.html", {"role": role, "content": content}
                ).body.decode()
                yield f"event: chat\ndata: {html}\n\n"
            else:
                yield f"event: {event_type}\ndata: {json.dumps(event)}\n\n"

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )
