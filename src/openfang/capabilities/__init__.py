"""Capability implementations for protocols.

Core adapters for file system, web browsing, memory, shell, projects,
conversations, and scheduling. Channels and skills are now at top-level.
"""

from .conversations import InMemoryConversations
from .cron import InMemoryCron
from .files import LocalFiles
from .memory import InMemoryMemory
from .projects import LocalProjects
from .shell import LocalShell
from .web import PlaywrightSession, PlaywrightWeb

__all__ = [
    "LocalFiles",
    "PlaywrightWeb",
    "PlaywrightSession",
    "InMemoryMemory",
    "LocalShell",
    "LocalProjects",
    "InMemoryConversations",
    "InMemoryCron",
]
