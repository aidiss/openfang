"""Cron routes."""

from __future__ import annotations

from fastapi import APIRouter, Request

from openfang.gateway.deps import CronDataDep, GatewayDep, get_cron_data, templates
from openfang.gateway.helpers import htmx_error, htmx_or_json, is_htmx

router = APIRouter(prefix="/cron", tags=["cron"])


@router.get("")
async def cron_list(request: Request, jobs: CronDataDep):
    """List cron jobs."""
    return htmx_or_json(request, templates, "partials/cron.html", {"jobs": jobs})


@router.post("")
async def cron_create(request: Request, gateway: GatewayDep):
    """Create a cron job."""
    form = await request.form()
    schedule = str(form.get("schedule", ""))
    task = str(form.get("task", ""))

    if not schedule or not task:
        return htmx_error(request, "Schedule and task required")

    job = await gateway.deps.scheduling.cron.create(schedule, task)

    if is_htmx(request):
        jobs = await get_cron_data(gateway)
        return templates.TemplateResponse(request, "partials/cron.html", {"jobs": jobs})
    return {"id": job.id, "schedule": job.schedule, "task": job.task, "enabled": job.enabled}


@router.delete("/{job_id}")
async def cron_delete(request: Request, job_id: str, gateway: GatewayDep):
    """Delete a cron job."""
    await gateway.deps.scheduling.cron.delete(job_id)

    if is_htmx(request):
        jobs = await get_cron_data(gateway)
        return templates.TemplateResponse(request, "partials/cron.html", {"jobs": jobs})
    return {"deleted": job_id}
