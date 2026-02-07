"""
OpenFang - AI agent gateway with pluggable adapters.

Usage:
    from src.spikes.deps import Deps, User, agent, chat, create_deps

Run modes:
    python -m src.spikes.deps           # CLI help
    python -m src.spikes.deps chat      # Interactive chat
    python -m src.spikes.deps telegram  # Telegram bot
    python -m src.spikes.deps cron      # Cron runner
"""

# Types and models
# Implementations
from .agent import TOOL_PERMISSIONS, create_agent, default_agent
from .capabilities import (
    FileSessions,
    InMemoryCron,
    InMemoryMemory,
    InMemorySessions,
    LocalFiles,
    LocalProjects,
    LocalShell,
    PlaywrightSession,
    PlaywrightWeb,
)
from .chat import DEFAULT_USAGE_LIMITS, chat, start_session

# Core
from .deps import (
    CommsAdapters,
    Deps,
    SchedulingAdapters,
    StorageAdapters,
    WebAdapters,
    WorkspaceAdapters,
    create_deps,
)
from .models import CronJob, User

# Protocols
from .protocols import (
    Cron,
    Files,
    Memory,
    Projects,
    Sessions,
    Shell,
    Web,
    WebSession,
)
from .types import Match, Page, Result


# Runners and Gateway (lazy import)
def __getattr__(name: str):
    if name in ("run_cron_checker", "run_cron_with_agent"):
        from .runners import cron

        return getattr(cron, name)
    if name == "run_telegram_bot":
        from .runners import telegram

        return getattr(telegram, name)
    if name in ("Gateway", "HeartbeatConfig", "serve"):
        from . import gateway

        return getattr(gateway, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Types
    "Match",
    "Page",
    "Result",
    # Models
    "CronJob",
    "User",
    # Protocols
    "Cron",
    "Files",
    "Memory",
    "Projects",
    "Sessions",
    "Shell",
    "Web",
    "WebSession",
    # Implementations
    "FileSessions",
    "InMemoryCron",
    "InMemoryMemory",
    "InMemorySessions",
    "LocalFiles",
    "LocalProjects",
    "LocalShell",
    "PlaywrightSession",
    "PlaywrightWeb",
    # Core
    "Deps",
    "create_deps",
    # Adapter groups
    "StorageAdapters",
    "WebAdapters",
    "WorkspaceAdapters",
    "SchedulingAdapters",
    "CommsAdapters",
    "default_agent",
    "create_agent",
    "TOOL_PERMISSIONS",
    "chat",
    "start_session",
    "DEFAULT_USAGE_LIMITS",
    # Runners
    "run_cron_checker",
    "run_cron_with_agent",
    "run_telegram_bot",
    # Gateway
    "Gateway",
    "HeartbeatConfig",
    "serve",
]
