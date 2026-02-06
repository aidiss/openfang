"""In-memory conversation storage."""

from pydantic_ai.messages import ModelMessage


class InMemoryConversations:
    """In-memory conversation storage."""

    def __init__(self):
        self._conversations: dict[str, list[ModelMessage]] = {}
        self._user_conversations: dict[int, set[str]] = {}

    async def get(self, conversation_id: str) -> list[ModelMessage]:
        return self._conversations.get(conversation_id, [])

    async def save(self, conversation_id: str, messages: list[ModelMessage]) -> None:
        self._conversations[conversation_id] = list(messages)

    async def append(self, conversation_id: str, messages: list[ModelMessage]) -> None:
        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = []
        self._conversations[conversation_id].extend(messages)

    async def delete(self, conversation_id: str) -> None:
        self._conversations.pop(conversation_id, None)
        for user_convs in self._user_conversations.values():
            user_convs.discard(conversation_id)

    async def list(self, user_id: int | None = None) -> list[str]:
        if user_id is None:
            return list(self._conversations.keys())
        return list(self._user_conversations.get(user_id, set()))

    def associate_user(self, conversation_id: str, user_id: int) -> None:
        if user_id not in self._user_conversations:
            self._user_conversations[user_id] = set()
        self._user_conversations[user_id].add(conversation_id)
