"""Subagent models - specs, run records, and results."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SubagentSpec(BaseModel):
    """Definition of a specialized subagent."""

    id: str
    """Unique identifier, e.g. 'code-analyzer'."""

    name: str
    """Human-readable name."""

    description: str
    """What this subagent does (shown to main agent for selection)."""

    system_prompt: str
    """Specialized instructions for this subagent."""

    model: str | None = None
    """Override model. If None, inherits from parent agent."""

    tools: list[str] | None = None
    """Allowed tool names. If None, uses all tools minus denied_tools."""

    denied_tools: list[str] = Field(default_factory=list)
    """Explicitly denied tools (applied after tools allowlist)."""

    max_requests: int = 10
    """Maximum API requests for safety."""


class SubagentRunRecord(BaseModel):
    """Tracks a running or completed subagent run."""

    run_id: str
    """Unique identifier for this run."""

    subagent_id: str
    """ID of the subagent spec used."""

    task: str
    """The task description given to the subagent."""

    label: str | None = None
    """Optional user-facing label."""

    parent_conversation_id: str | None = None
    """Conversation ID of the parent agent."""

    status: Literal["pending", "running", "completed", "failed", "timeout"] = "pending"
    """Current status of the run."""

    created_at: datetime = Field(default_factory=datetime.now)
    """When the run was created."""

    started_at: datetime | None = None
    """When execution started."""

    completed_at: datetime | None = None
    """When execution completed."""

    result: str | None = None
    """Final output from the subagent."""

    error: str | None = None
    """Error message if failed."""


class SubagentResult(BaseModel):
    """Result from a subagent execution."""

    run_id: str
    """The run ID for this execution."""

    status: Literal["success", "error", "timeout"]
    """Outcome status."""

    output: str | None = None
    """Final output from the subagent."""

    error: str | None = None
    """Error message if failed."""

    usage: dict | None = None
    """Token usage statistics."""
