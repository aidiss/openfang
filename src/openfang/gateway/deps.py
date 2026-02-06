"""Gateway dependencies - shared across all routes."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, Request
from fastapi.templating import Jinja2Templates

if TYPE_CHECKING:
    from .core import Gateway

# Templates directory
TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# =============================================================================
# Core dependencies
# =============================================================================


def get_gateway(request: Request) -> Gateway:
    """Get gateway instance from app state."""
    return request.app.state.gateway


GatewayDep = Annotated["Gateway", Depends(get_gateway)]


# =============================================================================
# Data fetchers
# =============================================================================


async def get_conversations_data(gw: GatewayDep) -> list[dict]:
    """Fetch all conversations with message counts."""
    conv_ids = await gw.deps.storage.conversations.list()
    convs = []
    for cid in conv_ids:
        msgs = await gw.deps.storage.conversations.get(cid)
        convs.append({"id": cid, "message_count": len(msgs)})
    return convs


async def get_cron_data(gw: GatewayDep) -> list[dict]:
    """Fetch all cron jobs as dicts."""
    jobs = await gw.deps.scheduling.cron.list()
    return [{"id": j.id, "schedule": j.schedule, "task": j.task, "enabled": j.enabled} for j in jobs]


async def get_memory_data(gw: GatewayDep) -> list[dict]:
    """Fetch all memory key-value pairs."""
    keys = await gw.deps.storage.memory.keys()
    items = []
    for k in keys:
        v = await gw.deps.storage.memory.get(k)
        items.append({"key": k, "value": v})
    return items


async def get_channels_data(gw: GatewayDep) -> list[dict]:
    """Fetch all channels with their accounts and status."""
    channels_data = []
    for ch_info in gw.deps.comms.channels.list_channels():
        # Check if channel is implemented (has `implemented` attr set to False means stub)
        channel = gw.deps.comms.channels.get_channel(ch_info.id)
        is_implemented = getattr(channel, "implemented", True) is not False

        accounts = await gw.deps.comms.channels.list_accounts(ch_info.id)
        statuses = await gw.deps.comms.channels.status()
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
