"""Gateway helper utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from fastapi.responses import HTMLResponse

if TYPE_CHECKING:
    from fastapi import Request
    from fastapi.templating import Jinja2Templates


def is_htmx(request: Request) -> bool:
    """Check if request is from HTMX."""
    return request.headers.get("HX-Request") == "true"


def htmx_or_json(
    request: Request,
    templates: Jinja2Templates,
    template_name: str,
    json_data: dict[str, Any],
    template_context: dict[str, Any] | None = None,
):
    """Return HTMX template response or JSON based on request type.

    Args:
        request: The FastAPI request.
        templates: Jinja2Templates instance.
        template_name: Template path for HTMX response.
        json_data: Data to return for JSON API requests.
        template_context: Additional context for template. If None, uses json_data.
    """
    if is_htmx(request):
        ctx = template_context or json_data
        return templates.TemplateResponse(request, template_name, ctx)
    return json_data


def htmx_error(request: Request, message: str) -> HTMLResponse | dict:
    """Return an error response appropriate for the request type.

    Args:
        request: The FastAPI request.
        message: Error message to display.
    """
    if is_htmx(request):
        return HTMLResponse(f"<div class='text-red-500 text-xs'>{message}</div>")
    return {"error": message}
