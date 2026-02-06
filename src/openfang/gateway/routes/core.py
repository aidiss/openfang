"""Core routes - index and health."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from openfang.gateway.deps import GatewayDep, templates
from openfang.gateway.helpers import htmx_or_json

router = APIRouter(tags=["core"])


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, gateway: GatewayDep):
    """Serve the chat interface."""
    return templates.TemplateResponse(request, "chat.html", {"conversation_id": gateway.deps.conversation_id})


@router.get("/health")
async def health(request: Request, gateway: GatewayDep):
    """Health check with heartbeat status."""
    data = {
        "status": "ok",
        "uptime": gateway.uptime,
        "heartbeat": {
            "enabled": gateway.heartbeat.enabled,
            "interval": gateway.heartbeat.interval,
            "last_at": gateway.last_heartbeat_at.isoformat() if gateway.last_heartbeat_at else None,
            "last_alert": gateway.last_heartbeat_alert[:200] if gateway.last_heartbeat_alert else None,
        },
    }
    return htmx_or_json(request, templates, "partials/health_badge.html", data)


@router.get("/overview")
async def overview(request: Request, gateway: GatewayDep):
    """Overview dashboard with gateway stats."""
    deps = gateway.deps

    # Calculate uptime in human-readable format
    uptime_secs = int(gateway.uptime)
    hours, remainder = divmod(uptime_secs, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{hours}h {minutes}m {seconds}s" if hours else f"{minutes}m {seconds}s"

    # Gather stats (skills.skills is an implementation detail not in protocol)
    all_skills = list(deps.comms.skills.skills.values())  # type: ignore[attr-defined]
    eligible_skills = deps.comms.skills.eligible_skills()
    memory_keys = await deps.storage.memory.keys()
    cron_jobs = await deps.scheduling.cron.list()
    conversation_ids = await deps.storage.conversations.list()
    channels = deps.comms.channels.list_channels()

    # Count active channel accounts
    statuses = await deps.comms.channels.status()
    active_channels = sum(1 for s in statuses if s.running)

    data = {
        "uptime": uptime_str,
        "uptime_secs": uptime_secs,
        "heartbeat_enabled": gateway.heartbeat.enabled,
        "heartbeat_interval": gateway.heartbeat.interval,
        "last_heartbeat": gateway.last_heartbeat_at.isoformat() if gateway.last_heartbeat_at else None,
        "skills_total": len(all_skills),
        "skills_active": len(eligible_skills),
        "memory_count": len(memory_keys),
        "cron_count": len(cron_jobs),
        "conversations_count": len(conversation_ids),
        "channels_total": len(channels),
        "channels_active": active_channels,
    }
    return htmx_or_json(request, templates, "partials/overview.html", data)
