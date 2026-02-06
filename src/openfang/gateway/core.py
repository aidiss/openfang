"""Gateway core - state and server entry point."""

from __future__ import annotations

import asyncio
import contextlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from .heartbeat import HeartbeatConfig, heartbeat_loop

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from ..deps import Deps


@dataclass
class Gateway:
    """Gateway state container."""

    deps: Deps
    heartbeat: HeartbeatConfig = field(default_factory=HeartbeatConfig)

    # State
    started_at: datetime = field(default_factory=datetime.now)
    last_heartbeat_at: datetime | None = None
    last_heartbeat_alert: str | None = None

    # Event queue for SSE
    _events: asyncio.Queue[dict[str, Any]] = field(default_factory=asyncio.Queue)
    _subscribers: int = 0

    @property
    def uptime(self) -> float:
        return (datetime.now() - self.started_at).total_seconds()

    def emit(self, event_type: str, **data: Any) -> None:
        """Emit an event to SSE subscribers."""
        event = {"type": event_type, "ts": datetime.now().isoformat(), **data}
        # Only queue if someone is listening
        if self._subscribers > 0:
            with contextlib.suppress(asyncio.QueueFull):
                self._events.put_nowait(event)

    async def events(self) -> AsyncIterator[dict[str, Any]]:
        """Async iterator for SSE events."""
        self._subscribers += 1
        try:
            while True:
                event = await self._events.get()
                yield event
        finally:
            self._subscribers -= 1


async def serve(
    gw: Gateway,
    host: str | None = None,
    port: int | None = None,
) -> None:
    """Run gateway HTTP server with heartbeat loop.

    Args:
        gw: Gateway state container.
        host: Bind address (default from settings).
        port: Port (default from settings).
    """
    import uvicorn

    from ..settings import settings
    from .app import app, init_app

    host = host or settings.host
    port = port or settings.port

    # Initialize app with gateway
    init_app(gw)

    # Start heartbeat in background
    heartbeat_task = asyncio.create_task(heartbeat_loop(gw))

    try:
        # Run HTTP server
        config = uvicorn.Config(
            app,
            host=host,
            port=port,
            log_level="info",
        )
        server = uvicorn.Server(config)
        await server.serve()
    finally:
        heartbeat_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await heartbeat_task
