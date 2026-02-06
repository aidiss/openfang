"""Cron job runner."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from datetime import datetime

from openfang.capabilities import InMemoryConversations
from openfang.chat import chat, start_conversation
from openfang.deps import create_deps
from openfang.models import CronJob, User
from openfang.protocols import Conversations, Cron


def cron_matches(schedule: str, dt: datetime) -> bool:
    """Simple cron matching (minute hour day month weekday)."""
    parts = schedule.split()
    if len(parts) != 5:
        return False

    minute, hour, day, month, weekday = parts
    checks = [
        (minute, dt.minute),
        (hour, dt.hour),
        (day, dt.day),
        (month, dt.month),
        (weekday, dt.weekday()),
    ]

    return all(not (pattern != "*" and pattern != str(value)) for pattern, value in checks)


async def run_cron_checker(
    cron: Cron,
    check_interval: int = 60,
    on_job: Callable[[CronJob], Awaitable[None]] | None = None,
):
    """
    Background cron job checker.

    Args:
        cron: Cron service to check jobs from
        check_interval: Seconds between checks
        on_job: Callback when a job should run
    """
    print(f"Cron checker starting (checking every {check_interval}s)...")

    while True:
        now = datetime.now()
        jobs = await cron.list()

        for job in jobs:
            if job.enabled and cron_matches(job.schedule, now):
                print(f"[CRON] Running job {job.id}: {job.task}")
                if on_job:
                    try:
                        await on_job(job)
                    except Exception as e:
                        print(f"[CRON] Job {job.id} failed: {e}")

        await asyncio.sleep(check_interval)


async def run_cron_with_agent(
    cron: Cron,
    conversations: Conversations | None = None,
    check_interval: int = 60,
):
    """
    Run cron checker that executes jobs via agent.

    Each job's task becomes a prompt for the agent.
    """

    conversations = conversations or InMemoryConversations()

    async def execute_job(job: CronJob):
        system_user = User(id=0, email="cron@system", roles={"admin", "developer"})

        async with create_deps(
            user=system_user,
            conversations=conversations,
            cron=cron,
        ) as deps:
            await start_conversation(deps, f"cron-{job.id}")
            response = await chat(deps, job.task)
            print(f"[CRON] Job {job.id} response: {response}")

    await run_cron_checker(cron, check_interval, on_job=execute_job)
