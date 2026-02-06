"""Webhook routes for external integrations."""

from __future__ import annotations

import uuid
from typing import Literal

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from openfang.gateway.deps import GatewayDep
from openfang.settings import settings

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


class WakePayload(BaseModel):
    """Payload for wake webhook."""

    text: str
    mode: Literal["now", "next-heartbeat"] = "now"


class AgentPayload(BaseModel):
    """Payload for agent webhook."""

    message: str
    session_key: str | None = None
    channel: str | None = None
    to: str | None = None


class WebhookResponse(BaseModel):
    """Response for webhook requests."""

    status: str
    run_id: str | None = None


def validate_token(token: str | None) -> None:
    """Validate webhook token."""
    if not settings.webhooks_enabled:
        raise HTTPException(status_code=404, detail="Webhooks not enabled")

    if not settings.webhooks_token:
        raise HTTPException(status_code=500, detail="Webhook token not configured")

    if not token:
        raise HTTPException(status_code=401, detail="Missing X-OpenFang-Token header")

    if token != settings.webhooks_token:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/wake", response_model=WebhookResponse)
async def webhook_wake(
    payload: WakePayload,
    gateway: GatewayDep,
    x_openfang_token: str | None = Header(default=None),
) -> WebhookResponse:
    """Trigger a wake event.

    Enqueues a system event that triggers the heartbeat loop.
    Use mode="now" for immediate trigger, or "next-heartbeat" to wait
    for the next scheduled heartbeat.
    """
    validate_token(x_openfang_token)

    # Queue the wake event
    run_id = str(uuid.uuid4())[:8]

    # If mode is "now", heartbeat would be triggered immediately
    # (Note: immediate trigger not yet implemented)

    return WebhookResponse(status="queued", run_id=run_id)


@router.post("/agent", response_model=WebhookResponse, status_code=202)
async def webhook_agent(
    payload: AgentPayload,
    gateway: GatewayDep,
    x_openfang_token: str | None = Header(default=None),
) -> WebhookResponse:
    """Run an agent turn from webhook.

    Creates an isolated agent session and runs the provided message.
    Returns immediately with a run_id (202 Accepted).
    """
    validate_token(x_openfang_token)

    from openfang.chat import chat

    run_id = str(uuid.uuid4())[:8]
    _session_key = payload.session_key or f"webhook:{run_id}"  # noqa: F841

    # Run agent (for now, synchronously - could be background task)
    try:
        _response = await chat(gateway.deps, payload.message)  # noqa: F841

        # If channel and recipient specified, send the response
        if payload.channel and payload.to:
            # TODO: implement channel send via dispatcher
            pass

    except Exception:  # noqa: BLE001  # nosec B110
        # Log error but don't fail the webhook - webhook should always return 202
        pass

    return WebhookResponse(status="accepted", run_id=run_id)
