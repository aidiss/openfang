"""SSE event helpers for gateway."""

from __future__ import annotations

import asyncio
import contextlib
from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any


def emit(state: Any, event_type: str, **data: Any) -> None:
    """Emit an event to SSE subscribers.

    Args:
        state: FastAPI app.state with events_queue and subscribers.
        event_type: Event type name.
        **data: Additional event data.
    """
    event = {"type": event_type, "ts": datetime.now().isoformat(), **data}
    if state.subscribers > 0:
        with contextlib.suppress(asyncio.QueueFull):
            state.events_queue.put_nowait(event)


async def events(state: Any) -> AsyncIterator[dict[str, Any]]:
    """Async iterator for SSE events.

    Args:
        state: FastAPI app.state with events_queue and subscribers.

    Yields:
        Event dictionaries.
    """
    state.subscribers += 1
    try:
        while True:
            event = await state.events_queue.get()
            yield event
    finally:
        state.subscribers -= 1
