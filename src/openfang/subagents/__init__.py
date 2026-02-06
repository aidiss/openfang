"""Subagent system - specialized task delegation.

This module provides:
- SubagentSpec: Definition of a specialized subagent
- SubagentRegistry: Loads and manages subagent specs
- SubagentExecutor: Runs subagent instances
- SUBAGENT_TOOLS: Tools for delegation (subagent_delegate, subagent_list)
"""

from .executor import SubagentExecutor
from .models import SubagentResult, SubagentRunRecord, SubagentSpec
from .registry import SubagentRegistry
from .tools import SUBAGENT_TOOLS, subagent_delegate, subagent_list

__all__ = [
    # Models
    "SubagentSpec",
    "SubagentRunRecord",
    "SubagentResult",
    # Registry
    "SubagentRegistry",
    # Executor
    "SubagentExecutor",
    # Tools
    "SUBAGENT_TOOLS",
    "subagent_delegate",
    "subagent_list",
]
