"""Gateway route modules."""

from .channels import router as channels_router
from .chat import router as chat_router
from .core import router as core_router
from .cron import router as cron_router
from .events import router as events_router
from .heartbeat import router as heartbeat_router
from .memory import router as memory_router
from .projects import router as projects_router
from .sessions import router as sessions_router
from .skills import router as skills_router
from .webhooks import router as webhooks_router

__all__ = [
    "channels_router",
    "chat_router",
    "core_router",
    "cron_router",
    "events_router",
    "heartbeat_router",
    "memory_router",
    "projects_router",
    "sessions_router",
    "skills_router",
    "webhooks_router",
]
