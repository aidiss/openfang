"""Memory routes."""

from __future__ import annotations

from fastapi import APIRouter, Request

from openfang.gateway.deps import GatewayDep, MemoryDataDep, get_memory_data, templates
from openfang.gateway.helpers import htmx_error, htmx_or_json, is_htmx

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("")
async def memory_list(request: Request, items: MemoryDataDep):
    """List memory keys with values."""
    return htmx_or_json(request, templates, "partials/memory.html", {"items": items})


@router.post("")
async def memory_set(request: Request, gateway: GatewayDep):
    """Set a memory key."""
    form = await request.form()
    key = str(form.get("key", ""))
    value = str(form.get("value", ""))

    if not key:
        return htmx_error(request, "Key required")

    await gateway.deps.storage.memory.set(key, value)

    if is_htmx(request):
        items = await get_memory_data(gateway)
        return templates.TemplateResponse(request, "partials/memory.html", {"items": items})
    return {"key": key, "value": value}


@router.delete("/{key}")
async def memory_delete(request: Request, key: str, gateway: GatewayDep):
    """Delete a memory key."""
    await gateway.deps.storage.memory.delete(key)

    if is_htmx(request):
        items = await get_memory_data(gateway)
        return templates.TemplateResponse(request, "partials/memory.html", {"items": items})
    return {"deleted": key}
