"""Gateway HTTP app - FastAPI with routers."""

from __future__ import annotations

from typing import TYPE_CHECKING

import logfire
from fastapi import FastAPI
from pydantic import BaseModel

from .routes import (
    channels_router,
    chat_router,
    conversations_router,
    core_router,
    cron_router,
    events_router,
    heartbeat_router,
    memory_router,
    projects_router,
    skills_router,
    webhooks_router,
)

if TYPE_CHECKING:
    from .core import Gateway


# =============================================================================
# Request/Response models
# =============================================================================


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


class HeartbeatStatus(BaseModel):
    enabled: bool
    interval: int
    last_at: str | None
    last_alert: str | None


class HeartbeatResult(BaseModel):
    ok: bool
    alert: str | None
    duration_ms: int


class HealthResponse(BaseModel):
    status: str
    uptime: float
    heartbeat: HeartbeatStatus


# =============================================================================
# App instance
# =============================================================================

app = FastAPI(
    title="OpenFang Gateway",
    description="HTTP gateway for AI agents with heartbeat",
    version="0.1.0",
)

# Instrument FastAPI with logfire
logfire.instrument_fastapi(app)

# Include all routers
app.include_router(core_router)
app.include_router(chat_router)
app.include_router(heartbeat_router)
app.include_router(conversations_router)
app.include_router(cron_router)
app.include_router(memory_router)
app.include_router(projects_router)
app.include_router(skills_router)
app.include_router(channels_router)
app.include_router(events_router)
app.include_router(webhooks_router)


# =============================================================================
# App initialization
# =============================================================================


def init_app(gw: Gateway) -> FastAPI:
    """Initialize app with gateway instance."""
    app.state.gateway = gw
    return app
