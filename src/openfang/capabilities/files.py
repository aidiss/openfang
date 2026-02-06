"""File operations on local filesystem.

This module implements the Files protocol for local filesystem access.
Methods are async for protocol compliance, enabling future implementations
(e.g., S3, remote filesystems) to use actual async I/O.
"""

from __future__ import annotations

import re
from pathlib import Path

from ..constants import MAX_SEARCH_RESULTS
from ..types import Match


class LocalFiles:
    """File operations scoped to a root directory.

    All paths are resolved relative to root unless absolute.
    Methods are async for protocol compatibility with remote implementations.
    """

    def __init__(self, root: Path):
        self.root = root

    def _resolve(self, path: str) -> Path:
        p = Path(path)
        return p if p.is_absolute() else self.root / p

    async def read(self, path: str) -> str:
        """Read file contents. Async for protocol compliance."""
        return self._resolve(path).read_text()

    async def write(self, path: str, content: str) -> None:
        """Write content to file, creating parent dirs. Async for protocol compliance."""
        p = self._resolve(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)

    async def list(self, pattern: str = "**/*") -> list[str]:
        """List files matching glob pattern. Excludes .git and .venv."""
        return [
            str(p.relative_to(self.root))
            for p in self.root.glob(pattern)
            if p.is_file() and ".git" not in p.parts and ".venv" not in p.parts
        ]

    async def search(self, pattern: str, file_glob: str = "**/*") -> list[Match]:
        """Search file contents with regex. Returns up to MAX_SEARCH_RESULTS matches."""
        matches = []
        regex = re.compile(pattern)
        for p in self.root.glob(file_glob):
            if not p.is_file() or ".git" in p.parts or ".venv" in p.parts:
                continue
            try:
                for i, line in enumerate(p.read_text().splitlines(), 1):
                    if regex.search(line):
                        matches.append(Match(str(p.relative_to(self.root)), i, line.strip()))
            except (UnicodeDecodeError, PermissionError):
                continue
        return matches[:MAX_SEARCH_RESULTS]
