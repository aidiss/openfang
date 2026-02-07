"""Domain models."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator, computed_field

PeerKind = Literal["direct", "group", "channel"]


def _validate_session_id(value: str) -> str:
    """Validate session ID format: {channel}:{account}:{peer_kind}:{peer_id}."""
    parts = value.split(":")
    if len(parts) != 4:
        raise ValueError(f"Invalid session ID format: {value!r} (expected channel:account:peer_kind:peer_id)")

    if parts[2] not in ("direct", "group", "channel"):
        raise ValueError(f"Invalid peer_kind: {parts[2]!r} (expected direct, group, or channel)")

    return value


SessionId = Annotated[str, BeforeValidator(_validate_session_id)]
"""Validated session ID string.

Format: {channel}:{account}:{peer_kind}:{peer_id}

Examples:
    - web:default:direct:main (default web session)
    - web:default:direct:a1b2c3d4 (user-created web session)
    - telegram:default:direct:123456789 (Telegram DM)
    - discord:main-bot:group:987654321 (Discord group)
"""


def session_id_web(peer_id: str = "main", account: str = "default") -> SessionId:
    """Create a web session ID."""
    return f"web:{account}:direct:{peer_id}"


def session_id_new(account: str = "default") -> SessionId:
    """Create a new web session with random ID."""
    return session_id_web(peer_id=uuid.uuid4().hex[:8], account=account)


def session_id_default() -> SessionId:
    """Default web session (main)."""
    return session_id_web("main")


class Session(BaseModel):
    """A chat session."""

    id: SessionId
    message_count: int = 0

    @computed_field
    @property
    def channel(self) -> str:
        return self.id.split(":")[0]

    @computed_field
    @property
    def account(self) -> str:
        return self.id.split(":")[1]

    @computed_field
    @property
    def peer_kind(self) -> PeerKind:
        return self.id.split(":")[2]  # type: ignore[return-value]

    @computed_field
    @property
    def peer_id(self) -> str:
        return self.id.split(":")[3]


class Role:
    """User role constants."""

    ADMIN = "admin"
    DEVELOPER = "developer"


@dataclass
class User:
    """Current user context."""

    id: int
    email: str
    roles: set[str] = field(default_factory=set)
    org_id: int | None = None
    phone: str | None = None
    telegram_id: str | None = None

    def has_role(self, role: str) -> bool:
        return role in self.roles

    @property
    def is_admin(self) -> bool:
        return Role.ADMIN in self.roles


@dataclass
class CronJob:
    """A scheduled job."""

    id: str
    schedule: str
    task: str
    enabled: bool = True
    created_by: int | None = None
