"""Heartbeat - periodic agent check-ins."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import logfire

from ..settings import settings
from . import sse

logger = logging.getLogger(__name__)


@dataclass
class HeartbeatResult:
    """Result of a heartbeat run."""

    ok: bool
    alert: str | None = None
    duration_ms: int = 0


def _create_heartbeat_deps():
    """Create deps for a heartbeat run."""
    from ..deps import CommsAdapters, Deps, SchedulingAdapters, StorageAdapters, WebAdapters, WorkspaceAdapters
    from ..models import User

    user = User(id=0, email="heartbeat@system", roles={"admin"})
    root = Path.cwd()

    return Deps(
        user=user,
        conversation_id="heartbeat",
        storage=StorageAdapters.default(root),
        web_adapters=WebAdapters.default(),
        workspace=WorkspaceAdapters.default(root),
        scheduling=SchedulingAdapters.default(),
        comms=CommsAdapters.default(),
    )


async def run_heartbeat(state: Any) -> HeartbeatResult:
    """Run a single heartbeat check.

    Args:
        state: FastAPI app.state with heartbeat config and SSE queue.
    """
    from ..chat import chat

    with logfire.span("heartbeat"):
        start = datetime.now()
        sse.emit(state, "heartbeat:start")

        try:
            # Create deps for this heartbeat run
            deps = _create_heartbeat_deps()

            response = await chat(deps, settings.heartbeat_prompt)
            duration_ms = int((datetime.now() - start).total_seconds() * 1000)

            # Check if it's an ack or an alert
            is_ack = (
                settings.heartbeat_ack_token in response and len(response.strip()) <= settings.heartbeat_ack_max_len
            )

            state.last_heartbeat_at = datetime.now()

            if is_ack:
                state.last_heartbeat_alert = None
                sse.emit(state, "heartbeat:ok", duration_ms=duration_ms)
                logfire.info("heartbeat ok", duration_ms=duration_ms)
                return HeartbeatResult(ok=True, duration_ms=duration_ms)
            else:
                state.last_heartbeat_alert = response
                sse.emit(state, "heartbeat:alert", alert=response[:500], duration_ms=duration_ms)
                logfire.warn("heartbeat alert", alert=response[:200], duration_ms=duration_ms)
                return HeartbeatResult(ok=False, alert=response, duration_ms=duration_ms)

        except Exception as e:
            duration_ms = int((datetime.now() - start).total_seconds() * 1000)
            sse.emit(state, "heartbeat:error", error=str(e), duration_ms=duration_ms)
            logfire.error("heartbeat error", error=str(e), duration_ms=duration_ms)
            logger.exception("Heartbeat failed")
            return HeartbeatResult(ok=False, alert=f"Error: {e}", duration_ms=duration_ms)


async def heartbeat_loop(state: Any) -> None:
    """Background heartbeat loop.

    Args:
        state: FastAPI app.state with SSE queue and heartbeat timestamps.
    """
    if not settings.heartbeat_enabled:
        logger.info("Heartbeat disabled")
        return

    logger.info(f"Heartbeat loop started (interval: {settings.heartbeat_interval}s)")

    while True:
        try:
            result = await run_heartbeat(state)
            status = "ok" if result.ok else f"alert: {(result.alert or 'unknown')[:50]}..."
            logger.info(f"Heartbeat: {status} ({result.duration_ms}ms)")
        except asyncio.CancelledError:
            break
        except Exception:
            logger.exception("Heartbeat loop error")

        await asyncio.sleep(settings.heartbeat_interval)
