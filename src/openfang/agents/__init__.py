"""Top-level agent system - configurable personas.

This module provides:
- AgentConfig: Configuration for a top-level agent
- AgentIdentity: Agent display identity (name, emoji)
- AgentToolPolicy: Tool access policy
- AgentRegistry: Loads and manages agent configs
"""

from .models import AgentConfig, AgentIdentity, AgentToolPolicy
from .registry import AgentRegistry

__all__ = [
    # Models
    "AgentConfig",
    "AgentIdentity",
    "AgentToolPolicy",
    # Registry
    "AgentRegistry",
]
