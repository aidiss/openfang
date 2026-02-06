"""Domain models."""

from dataclasses import dataclass, field


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
