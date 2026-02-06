"""In-memory key-value store."""

from __future__ import annotations


class InMemoryMemory:
    """In-memory key-value store."""

    def __init__(self):
        self._store: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        return self._store.get(key)

    async def set(self, key: str, value: str) -> None:
        self._store[key] = value

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)

    async def keys(self, prefix: str = "") -> list[str]:
        return [k for k in self._store if k.startswith(prefix)]
