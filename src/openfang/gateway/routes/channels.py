"""Channels routes."""

from __future__ import annotations

from fastapi import APIRouter, Request

from openfang.channels import ChannelAccount
from openfang.gateway.deps import ChannelsDep, ChannelsDataDep, get_channels_data, templates
from openfang.gateway.helpers import htmx_error, htmx_or_json, is_htmx

router = APIRouter(prefix="/channels", tags=["channels"])


@router.get("")
async def channels_list(request: Request, channels_data: ChannelsDataDep):
    """List all channels with their accounts and status."""
    return htmx_or_json(request, templates, "partials/channels.html", {"channels": channels_data})


@router.post("/{channel_id}/accounts")
async def channel_add_account(request: Request, channel_id: str, channels: ChannelsDep):
    """Add an account to a channel."""
    form = await request.form()
    account_id = str(form.get("id", "")).strip()
    token = str(form.get("token", "")).strip()
    name = str(form.get("name", "")).strip() or None

    if not account_id or not token:
        return htmx_error(request, "ID and token required")

    # Configure the channel implementation
    channel = channels.get_channel(channel_id)
    if channel:
        configure = getattr(channel, "configure_account", None)
        if configure:
            configure(account_id, token, name)

    # Add to registry
    account = ChannelAccount(
        id=account_id,
        channel_id=channel_id,
        name=name,
        config={"token": token},
    )
    await channels.add_account(account)

    if is_htmx(request):
        cdata = await get_channels_data(channels)
        return htmx_or_json(request, templates, "partials/channels.html", {"channels": cdata})
    return {"added": account_id}


@router.delete("/{channel_id}/accounts/{account_id}")
async def channel_remove_account(request: Request, channel_id: str, account_id: str, channels: ChannelsDep):
    """Remove an account from a channel."""
    await channels.remove_account(channel_id, account_id)

    # Also remove from channel implementation
    channel = channels.get_channel(channel_id)
    if channel:
        remove = getattr(channel, "remove_account", None)
        if remove:
            remove(account_id)

    if is_htmx(request):
        cdata = await get_channels_data(channels)
        return htmx_or_json(request, templates, "partials/channels.html", {"channels": cdata})
    return {"removed": account_id}


@router.post("/{channel_id}/accounts/{account_id}/start")
async def channel_start_account(request: Request, channel_id: str, account_id: str, channels: ChannelsDep):
    """Start a channel account."""
    try:
        await channels.start_account(channel_id, account_id)
    except Exception as e:
        return htmx_error(request, f"Error: {e}")

    if is_htmx(request):
        cdata = await get_channels_data(channels)
        return htmx_or_json(request, templates, "partials/channels.html", {"channels": cdata})
    return {"started": account_id}


@router.post("/{channel_id}/accounts/{account_id}/stop")
async def channel_stop_account(request: Request, channel_id: str, account_id: str, channels: ChannelsDep):
    """Stop a channel account."""
    await channels.stop_account(channel_id, account_id)

    if is_htmx(request):
        cdata = await get_channels_data(channels)
        return htmx_or_json(request, templates, "partials/channels.html", {"channels": cdata})
    return {"stopped": account_id}
