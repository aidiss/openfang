"""In-memory session storage."""

from pydantic_ai.messages import ModelMessage


class InMemorySessions:
    """In-memory session storage."""

    def __init__(self):
        self._sessions: dict[str, list[ModelMessage]] = {}
        self._user_sessions: dict[int, set[str]] = {}

    async def get(self, session_id: str) -> list[ModelMessage]:
        return self._sessions.get(session_id, [])

    async def save(self, session_id: str, messages: list[ModelMessage]) -> None:
        self._sessions[session_id] = list(messages)

    async def append(self, session_id: str, messages: list[ModelMessage]) -> None:
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        self._sessions[session_id].extend(messages)

    async def delete(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)
        for user_sessions in self._user_sessions.values():
            user_sessions.discard(session_id)

    async def list(self, user_id: int | None = None) -> list[str]:
        if user_id is None:
            return list(self._sessions.keys())
        return list(self._user_sessions.get(user_id, set()))

    def associate_user(self, session_id: str, user_id: int) -> None:
        if user_id not in self._user_sessions:
            self._user_sessions[user_id] = set()
        self._user_sessions[user_id].add(session_id)
