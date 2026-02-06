"""Chat routes."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from openfang.chat import chat as do_chat
from openfang.gateway.deps import GatewayDep, templates
from openfang.gateway.helpers import is_htmx

router = APIRouter(tags=["chat"])


class ChatResponse(BaseModel):
    response: str


@router.post("/chat")
async def chat(request: Request, gateway: GatewayDep):
    """Send a message to the agent."""
    htmx = is_htmx(request)

    if htmx:
        form = await request.form()
        user_message = str(form.get("message", ""))
    else:
        body = await request.json()
        user_message = str(body.get("message", ""))

    if not user_message:
        return {"error": "No message provided"}

    response = await do_chat(gateway.deps, user_message)

    if htmx:
        user_html = templates.TemplateResponse(
            request, "partials/message.html", {"role": "user", "content": user_message}
        ).body.decode()
        assistant_html = templates.TemplateResponse(
            request, "partials/message.html", {"role": "assistant", "content": response}
        ).body.decode()
        return HTMLResponse(content=user_html + assistant_html)

    return ChatResponse(response=response)
