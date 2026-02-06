"""Heartbeat - periodic agent check-ins."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

import logfire

if TYPE_CHECKING:
    from .core import Gateway

logger = logging.getLogger(__name__)


@dataclass
class HeartbeatConfig:
    """Heartbeat configuration."""

    enabled: bool = True
    interval: int = 1800  # 30 minutes
    prompt: str = "Check HEARTBEAT.md if it exists. If nothing needs attention, reply exactly: HEARTBEAT_OK"
    ack_token: str = "HEARTBEAT_OK"
    ack_max_len: int = 300


@dataclass
class HeartbeatResult:
    """Result of a heartbeat run."""

    ok: bool
    alert: str | None = None
    duration_ms: int = 0


async def run_heartbeat(gw: Gateway) -> HeartbeatResult:
    """Run a single heartbeat check."""
    from ..chat import chat

    with logfire.span("heartbeat"):
        start = datetime.now()
        gw.emit("heartbeat:start")

        try:
            response = await chat(gw.deps, gw.heartbeat.prompt)
            duration_ms = int((datetime.now() - start).total_seconds() * 1000)

            # Check if it's an ack or an alert
            is_ack = gw.heartbeat.ack_token in response and len(response.strip()) <= gw.heartbeat.ack_max_len

            gw.last_heartbeat_at = datetime.now()

            if is_ack:
                gw.last_heartbeat_alert = None
                gw.emit("heartbeat:ok", duration_ms=duration_ms)
                logfire.info("heartbeat ok", duration_ms=duration_ms)
                return HeartbeatResult(ok=True, duration_ms=duration_ms)
            else:
                gw.last_heartbeat_alert = response
                gw.emit("heartbeat:alert", alert=response[:500], duration_ms=duration_ms)
                logfire.warn("heartbeat alert", alert=response[:200], duration_ms=duration_ms)
                return HeartbeatResult(ok=False, alert=response, duration_ms=duration_ms)

        except Exception as e:
            duration_ms = int((datetime.now() - start).total_seconds() * 1000)
            gw.emit("heartbeat:error", error=str(e), duration_ms=duration_ms)
            logfire.error("heartbeat error", error=str(e), duration_ms=duration_ms)
            logger.exception("Heartbeat failed")
            return HeartbeatResult(ok=False, alert=f"Error: {e}", duration_ms=duration_ms)


async def heartbeat_loop(gw: Gateway) -> None:
    """Background heartbeat loop."""
    if not gw.heartbeat.enabled:
        logger.info("Heartbeat disabled")
        return

    logger.info(f"Heartbeat loop started (interval: {gw.heartbeat.interval}s)")

    while True:
        try:
            result = await run_heartbeat(gw)
            status = "ok" if result.ok else f"alert: {result.alert[:50]}..."
            logger.info(f"Heartbeat: {status} ({result.duration_ms}ms)")
        except asyncio.CancelledError:
            break
        except Exception:
            logger.exception("Heartbeat loop error")

        await asyncio.sleep(gw.heartbeat.interval)
