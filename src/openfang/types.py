"""Data types used across the deps package."""

from dataclasses import dataclass


@dataclass
class Page:
    """Snapshot of a web page."""

    url: str
    title: str
    text: str
    html: str


@dataclass
class Match:
    """Search result from grep."""

    path: str
    line: int
    text: str


@dataclass
class Result:
    """Shell command result."""

    code: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.code == 0
