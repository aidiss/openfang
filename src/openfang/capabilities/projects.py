"""Local project management."""

from pathlib import Path


class LocalProjects:
    """Manage multiple local projects."""

    def __init__(self):
        self._projects: dict[str, Path] = {}
        self._current: str | None = None

    async def current(self) -> tuple[str, Path] | None:
        if self._current is None:
            return None
        return (self._current, self._projects[self._current])

    async def switch(self, project_id: str) -> Path:
        if project_id not in self._projects:
            raise KeyError(f"Project not found: {project_id}")
        self._current = project_id
        return self._projects[project_id]

    async def list(self) -> list[str]:
        return list(self._projects.keys())

    async def register(self, project_id: str, path: Path) -> None:
        self._projects[project_id] = path.resolve()
        if self._current is None:
            self._current = project_id
