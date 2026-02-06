"""Gateway dependencies - shared across all routes."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any

from fastapi import Depends, Request
from fastapi.templating import Jinja2Templates

if TYPE_CHECKING:
    from ..deps import Deps

# Templates directory
TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# =============================================================================
# Core dependencies
# =============================================================================


def _create_deps(conversation_id: str = "web-session") -> Deps:
    """Create deps for an HTTP request.

    Each request gets fresh deps with the specified conversation.
    """
    from ..deps import CommsAdapters, Deps, SchedulingAdapters, StorageAdapters, WebAdapters, WorkspaceAdapters
    from ..models import User

    user = User(id=0, email="web@system", roles={"admin"})
    root = Path.cwd()

    return Deps(
        user=user,
        conversation_id=conversation_id,
        storage=StorageAdapters.default(root),
        web_adapters=WebAdapters.default(),
        workspace=WorkspaceAdapters.default(root),
        scheduling=SchedulingAdapters.default(),
        comms=CommsAdapters.default(),
    )


def get_deps(request: Request) -> Deps:
    """Create deps for this request.

    Note: Creates fresh deps per-request. For testing, override this dependency.
    """
    return _create_deps()


def get_state(request: Request) -> Any:
    """Get full app.state for routes needing heartbeat/SSE state."""
    return request.app.state


def get_channels(request: Request):
    """Get channels registry from app state."""
    return request.app.state.channels


def uptime(request: Request) -> float:
    """Get server uptime in seconds."""
    started_at: datetime = request.app.state.started_at
    return (datetime.now() - started_at).total_seconds()


DepsDep = Annotated["Deps", Depends(get_deps)]
StateDep = Annotated[Any, Depends(get_state)]
ChannelsDep = Annotated[Any, Depends(get_channels)]
UptimeDep = Annotated[float, Depends(uptime)]


# =============================================================================
# Data fetchers
# =============================================================================


async def get_conversations_data(deps: DepsDep) -> list[dict]:
    """Fetch all conversations with message counts."""
    conv_ids = await deps.storage.conversations.list()
    convs = []
    for cid in conv_ids:
        msgs = await deps.storage.conversations.get(cid)
        convs.append({"id": cid, "message_count": len(msgs)})
    return convs


async def get_cron_data(deps: DepsDep) -> list[dict]:
    """Fetch all cron jobs as dicts."""
    jobs = await deps.scheduling.cron.list()
    return [{"id": j.id, "schedule": j.schedule, "task": j.task, "enabled": j.enabled} for j in jobs]


async def get_memory_data(deps: DepsDep) -> list[dict]:
    """Fetch all memory key-value pairs."""
    keys = await deps.storage.memory.keys()
    items = []
    for k in keys:
        v = await deps.storage.memory.get(k)
        items.append({"key": k, "value": v})
    return items


async def get_channels_data(channels: ChannelsDep) -> list[dict]:
    """Fetch all channels with their accounts and status."""
    channels_data = []
    for ch_info in channels.list_channels():
        # Check if channel is implemented (has `implemented` attr set to False means stub)
        channel = channels.get_channel(ch_info.id)
        is_implemented = getattr(channel, "implemented", True) is not False

        accounts = await channels.list_accounts(ch_info.id)
        statuses = await channels.status()
        status_map = {s.account_id: s for s in statuses if s.channel_id == ch_info.id}

        account_data = [
            {
                "id": acc.id,
                "name": acc.name or acc.id,
                "enabled": acc.enabled,
                "running": st.running if (st := status_map.get(acc.id)) else False,
                "connected": st.connected if st else False,
                "last_error": st.last_error if st else None,
            }
            for acc in accounts
        ]

        channels_data.append(
            {
                "id": ch_info.id,
                "name": ch_info.name,
                "emoji": ch_info.emoji,
                "description": ch_info.description,
                "config_fields": ch_info.config_fields,
                "accounts": account_data,
                "implemented": is_implemented,
            }
        )
    return channels_data


# =============================================================================
# Dependency type aliases
# =============================================================================

ConversationsDataDep = Annotated[list[dict], Depends(get_conversations_data)]
CronDataDep = Annotated[list[dict], Depends(get_cron_data)]
MemoryDataDep = Annotated[list[dict], Depends(get_memory_data)]
ChannelsDataDep = Annotated[list[dict], Depends(get_channels_data)]
