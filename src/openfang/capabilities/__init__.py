"""Capability implementations for protocols.

Core adapters for file system, web browsing, memory, shell, projects,
sessions, and scheduling. Channels and skills are now at top-level.
"""

from .cron import InMemoryCron
from .file_sessions import FileSessions
from .files import LocalFiles
from .memory import InMemoryMemory
from .projects import LocalProjects
from .sessions import InMemorySessions
from .shell import LocalShell
from .web import PlaywrightSession, PlaywrightWeb

__all__ = [
    "LocalFiles",
    "PlaywrightWeb",
    "PlaywrightSession",
    "InMemoryMemory",
    "LocalShell",
    "LocalProjects",
    "InMemorySessions",
    "FileSessions",
    "InMemoryCron",
]
