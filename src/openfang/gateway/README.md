# Gateway

FastAPI HTTP server providing REST API and web UI.

- **API docs:** `/docs` (auto-generated OpenAPI)
- **Web UI:** `/` (HTMX-powered dashboard)
- **SSE events:** `/events` (real-time updates)

Key files:
- `app.py` - FastAPI setup, router registration
- `core.py` - `Gateway` class, `serve()` function
- `routes/` - Modular endpoints (chat, channels, skills, cron, etc.)
- `templates/` - Jinja2 HTML templates
