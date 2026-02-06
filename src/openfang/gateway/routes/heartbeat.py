"""Heartbeat routes."""

from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

from openfang.gateway.deps import StateDep, templates
from openfang.gateway.heartbeat import run_heartbeat
from openfang.gateway.helpers import htmx_or_json

router = APIRouter(prefix="/heartbeat", tags=["heartbeat"])


class HeartbeatStatus(BaseModel):
    enabled: bool
    interval: int
    last_at: str | None
    last_alert: str | None


@router.get("", response_model=HeartbeatStatus)
async def heartbeat_status(state: StateDep):
    """Get heartbeat status."""
    return {
        "enabled": state.heartbeat.enabled,
        "interval": state.heartbeat.interval,
        "last_at": state.last_heartbeat_at.isoformat() if state.last_heartbeat_at else None,
        "last_alert": state.last_heartbeat_alert,
    }


@router.post("/run")
async def heartbeat_run(request: Request, state: StateDep):
    """Trigger immediate heartbeat check."""
    result = await run_heartbeat(state)
    data = {"ok": result.ok, "alert": result.alert, "duration_ms": result.duration_ms}
    return htmx_or_json(request, templates, "partials/heartbeat.html", data)
