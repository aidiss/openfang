"""Gateway HTTP app - FastAPI with clean lifespan."""

from __future__ import annotations

import asyncio
import contextlib
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime
from openfang.channels import ChannelRegistry
from openfang.messaging import MessageDispatcher, RouteResolver
import logfire
from fastapi import FastAPI

from .heartbeat import heartbeat_loop
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

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage gateway lifecycle: channels, dispatcher, heartbeat."""
    # Runtime state (initialized when server starts)
    app.state.started_at = datetime.now()
    app.state.last_heartbeat_at = None
    app.state.last_heartbeat_alert = None
    app.state.events_queue = asyncio.Queue()
    app.state.subscribers = 0

    # Infrastructure
    channels = ChannelRegistry.default()
    dispatcher = MessageDispatcher(channels=channels, resolver=RouteResolver())
    channels.set_message_handler(dispatcher.handle_message)
    await channels.start_all()
    app.state.channels = channels
    app.state.dispatcher = dispatcher

    heartbeat_task = asyncio.create_task(heartbeat_loop(app.state))
    logger.info("Gateway started")

    yield

    heartbeat_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await heartbeat_task
    await channels.stop_all()
    logger.info("Gateway stopped")


def create_app() -> FastAPI:
    """Create FastAPI app."""
    app = FastAPI(
        title="OpenFang Gateway",
        description="HTTP gateway for AI agents with heartbeat",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Instrument and add routers
    logfire.instrument_fastapi(app)
    for router in [
        core_router,
        chat_router,
        heartbeat_router,
        conversations_router,
        cron_router,
        memory_router,
        projects_router,
        skills_router,
        channels_router,
        events_router,
        webhooks_router,
    ]:
        app.include_router(router)

    return app
