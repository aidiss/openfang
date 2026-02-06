"""Shell execution on local system."""

from __future__ import annotations

import asyncio
import subprocess  # nosec B404 - subprocess is required for shell execution
from pathlib import Path

from ..types import Result


class LocalShell:
    """Execute commands locally."""

    def __init__(self, default_cwd: Path | None = None):
        self._cwd = default_cwd or Path.cwd()

    async def exec(self, cmd: str, cwd: Path | None = None) -> Result:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            cwd=cwd or self._cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        return Result(
            code=proc.returncode or 0,
            stdout=stdout.decode(errors="replace"),
            stderr=stderr.decode(errors="replace"),
        )
