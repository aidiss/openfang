"""Subagent executor - creates and runs subagent instances."""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic_ai import Agent, RunContext, UsageLimits

from .models import SubagentResult, SubagentRunRecord, SubagentSpec

if TYPE_CHECKING:
    from ..deps import Deps


@dataclass
class SubagentExecutor:
    """Executes subagent runs with lifecycle management."""

    parent_model: str | None = None
    """Model to use if subagent doesn't specify one."""

    _active_runs: dict[str, SubagentRunRecord] = field(default_factory=dict)
    """Currently active runs indexed by run_id."""

    async def run_sync(
        self,
        spec: SubagentSpec,
        task: str,
        deps: Deps,
        timeout_seconds: int = 300,
    ) -> SubagentResult:
        """Run a subagent synchronously, waiting for result.

        Args:
            spec: The subagent specification.
            task: The task description for the subagent.
            deps: Parent deps (will be sandboxed for subagent).
            timeout_seconds: Maximum time to wait.

        Returns:
            SubagentResult with status, output, and usage.
        """
        run_id = str(uuid.uuid4())[:8]
        record = SubagentRunRecord(
            run_id=run_id,
            subagent_id=spec.id,
            task=task,
            parent_conversation_id=deps.conversation_id,
            status="running",
            created_at=datetime.now(),
            started_at=datetime.now(),
        )
        self._active_runs[run_id] = record

        try:
            # Create sandboxed deps for subagent
            subagent_deps = self._create_subagent_deps(deps, run_id)

            # Create the subagent
            agent = self._create_agent(spec)

            # Run with timeout
            result = await asyncio.wait_for(
                agent.run(
                    task,
                    deps=subagent_deps,
                    usage_limits=UsageLimits(request_limit=spec.max_requests),
                ),
                timeout=timeout_seconds,
            )

            # Success
            record.status = "completed"
            record.completed_at = datetime.now()
            record.result = result.output

            # Get usage info
            usage_info = result.usage()
            usage_dict = None
            if usage_info:
                usage_dict = {
                    "requests": usage_info.requests,
                    "request_tokens": usage_info.request_tokens,
                    "response_tokens": usage_info.response_tokens,
                    "total_tokens": usage_info.total_tokens,
                }

            return SubagentResult(
                run_id=run_id,
                status="success",
                output=result.output,
                usage=usage_dict,
            )

        except TimeoutError:
            record.status = "timeout"
            record.completed_at = datetime.now()
            record.error = f"Timeout after {timeout_seconds}s"
            return SubagentResult(
                run_id=run_id,
                status="timeout",
                error=f"Subagent timed out after {timeout_seconds} seconds",
            )

        except Exception as e:
            record.status = "failed"
            record.completed_at = datetime.now()
            record.error = str(e)
            return SubagentResult(
                run_id=run_id,
                status="error",
                error=str(e),
            )

        finally:
            # Remove from active runs
            self._active_runs.pop(run_id, None)

    def list_active(self, conversation_id: str | None = None) -> list[SubagentRunRecord]:
        """List active subagent runs.

        Args:
            conversation_id: Filter by parent conversation ID. If None, returns all.

        Returns:
            List of active run records.
        """
        runs = list(self._active_runs.values())
        if conversation_id:
            runs = [r for r in runs if r.parent_conversation_id == conversation_id]
        return runs

    def _create_agent(self, spec: SubagentSpec) -> Agent[Deps, str]:
        """Create a pydantic-ai Agent from a subagent spec."""
        from ..tools import ALL_TOOLS

        # Determine model
        model = spec.model or self.parent_model or "openai:gpt-4o-mini"

        # Create agent with subagent's system prompt
        agent: Agent[Deps, str] = Agent(
            model,
            deps_type=Deps,
            system_prompt=spec.system_prompt,
        )

        # Register only allowed tools
        allowed_tools = self._filter_tools(spec, ALL_TOOLS)
        for tool_func in allowed_tools:
            agent.tool(tool_func)

        return agent

    def _filter_tools(self, spec: SubagentSpec, all_tools: list) -> list:
        """Filter tools based on subagent spec's allow/deny lists."""
        # Get tool names
        tool_map = {t.__name__: t for t in all_tools}

        # Subagent tools should never be available to subagents
        subagent_tool_names = {"subagent_delegate", "subagent_list", "subagent_status", "subagent_cancel"}

        if spec.tools is not None:
            # Explicit allowlist
            allowed_names = set(spec.tools) - subagent_tool_names
        else:
            # All tools minus denied
            allowed_names = set(tool_map.keys()) - subagent_tool_names

        # Apply deny list
        allowed_names -= set(spec.denied_tools)

        return [tool_map[name] for name in allowed_names if name in tool_map]

    def _create_subagent_deps(self, parent_deps: Deps, run_id: str) -> Deps:
        """Create sandboxed deps for subagent execution."""
        from dataclasses import replace

        # Clone parent deps with subagent flags
        return replace(
            parent_deps,
            is_subagent=True,
            parent_run_id=run_id,
            # Subagents don't get access to subagent registry/executor
            subagents=None,
            subagent_executor=None,
        )
