"""In-memory cron job storage."""

from __future__ import annotations

from ..models import CronJob


class InMemoryCron:
    """In-memory cron job storage."""

    def __init__(self):
        self._jobs: dict[str, CronJob] = {}
        self._counter = 0

    async def create(self, schedule: str, task: str, user_id: int | None = None) -> CronJob:
        self._counter += 1
        job = CronJob(
            id=f"job-{self._counter}",
            schedule=schedule,
            task=task,
            enabled=True,
            created_by=user_id,
        )
        self._jobs[job.id] = job
        return job

    async def get(self, job_id: str) -> CronJob | None:
        return self._jobs.get(job_id)

    async def list(self, user_id: int | None = None) -> list[CronJob]:
        jobs = list(self._jobs.values())
        if user_id is not None:
            jobs = [j for j in jobs if j.created_by == user_id]
        return jobs

    async def delete(self, job_id: str) -> bool:
        return self._jobs.pop(job_id, None) is not None

    async def enable(self, job_id: str) -> bool:
        job = self._jobs.get(job_id)
        if job:
            job.enabled = True
            return True
        return False

    async def disable(self, job_id: str) -> bool:
        job = self._jobs.get(job_id)
        if job:
            job.enabled = False
            return True
        return False
