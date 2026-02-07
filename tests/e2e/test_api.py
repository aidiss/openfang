"""Fast API endpoint tests via httpx.AsyncClient.

These tests don't require a running server or browser - they use ASGITransport
to test the FastAPI app directly. Much faster than browser E2E tests.
"""

from __future__ import annotations

from httpx import AsyncClient
from pydantic_ai import ModelResponse, TextPart
from pydantic_ai.messages import ModelMessage
from pydantic_ai.models.function import AgentInfo, FunctionModel

from openfang.agent import default_agent


class TestCoreEndpoints:
    """Test core routes: index, health, overview."""

    async def test_index_returns_html(self, client: AsyncClient):
        """Home page returns HTML with chat interface."""
        response = await client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "OPENFANG" in response.text

    async def test_health_returns_json(self, client: AsyncClient):
        """Health endpoint returns JSON status."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "uptime" in data
        assert "heartbeat" in data

    async def test_health_returns_htmx_partial(self, client: AsyncClient):
        """Health endpoint returns HTML partial for HTMX requests."""
        response = await client.get("/health", headers={"HX-Request": "true"})
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    async def test_overview_returns_stats(self, client: AsyncClient):
        """Overview returns gateway statistics."""
        response = await client.get("/overview")
        assert response.status_code == 200
        data = response.json()
        assert "uptime" in data
        assert "skills_total" in data
        assert "memory_count" in data


class TestMemoryEndpoints:
    """Test memory CRUD endpoints."""

    async def test_memory_list_empty(self, client: AsyncClient):
        """Memory list returns empty initially."""
        response = await client.get("/memory")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []

    async def test_memory_set_and_get(self, client: AsyncClient):
        """Can set and retrieve memory values."""
        # Set a value (uses form data, not JSON)
        response = await client.post(
            "/memory",
            data={"key": "test-key", "value": "test-value"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200

        # List should include it
        response = await client.get("/memory")
        assert response.status_code == 200
        data = response.json()
        assert any(item["key"] == "test-key" for item in data["items"])

    async def test_memory_delete(self, client: AsyncClient):
        """Can delete memory values."""
        # Set a value first (uses form data)
        await client.post(
            "/memory",
            data={"key": "to-delete", "value": "temp"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # Delete it
        response = await client.delete("/memory/to-delete")
        assert response.status_code == 200

        # Should be gone
        response = await client.get("/memory")
        data = response.json()
        assert not any(item["key"] == "to-delete" for item in data["items"])


class TestChatEndpoint:
    """Test chat endpoint with mocked model."""

    async def test_chat_requires_message(self, client: AsyncClient):
        """Chat endpoint requires a message."""
        response = await client.post("/chat", json={"message": ""})
        assert response.status_code == 200
        data = response.json()
        assert "error" in data

    async def test_chat_with_mock_model(self, client: AsyncClient):
        """Chat returns response with FunctionModel override."""

        async def echo_model(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
            """Simple model that echoes the user message."""
            return ModelResponse(parts=[TextPart("Hello from test model!")])

        with default_agent.override(model=FunctionModel(echo_model)):
            response = await client.post("/chat", json={"message": "Hello!"})

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "Hello from test model!" in data["response"]

    async def test_chat_htmx_returns_html(self, client: AsyncClient):
        """Chat returns HTML messages for HTMX requests."""

        async def echo_model(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
            return ModelResponse(parts=[TextPart("HTMX response")])

        with default_agent.override(model=FunctionModel(echo_model)):
            response = await client.post(
                "/chat",
                data={"message": "Hello!"},
                headers={"HX-Request": "true", "Content-Type": "application/x-www-form-urlencoded"},
            )
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        # Should contain user and assistant message HTML
        assert "Hello!" in response.text


class TestSessionsEndpoints:
    """Test session management endpoints."""

    async def test_sessions_list(self, client: AsyncClient):
        """Can list sessions."""
        response = await client.get("/sessions")
        assert response.status_code == 200
        data = response.json()
        # Returns {"sessions": [...], "current_id": ...}
        assert "sessions" in data
        assert "current_id" in data

    async def test_session_create_and_switch(self, client: AsyncClient):
        """Can create and switch sessions."""
        # Create a new session (uses form data)
        response = await client.post(
            "/sessions",
            data={"id": "new-session"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200

        # Switch to it
        response = await client.post("/sessions/new-session/switch")
        assert response.status_code == 200

    async def test_session_messages(self, client: AsyncClient):
        """Can get messages for a session."""
        # Create a session first
        response = await client.post(
            "/sessions",
            data={"id": "msg-test-session"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200

        # Get messages for the session (should be empty initially)
        response = await client.get("/sessions/msg-test-session/messages")
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["session_id"] == "msg-test-session"
        assert "messages" in data
        assert data["messages"] == []

    async def test_session_switch_sets_cookie(self, client: AsyncClient):
        """Session switch sets session_id cookie."""
        # Create a session
        response = await client.post(
            "/sessions",
            data={"id": "cookie-test"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200

        # Switch to it - should set cookie
        response = await client.post("/sessions/cookie-test/switch")
        assert response.status_code == 200
        # Check cookie was set
        assert "session_id" in response.cookies
        assert response.cookies["session_id"] == "cookie-test"


class TestSkillsEndpoint:
    """Test skills listing endpoint."""

    async def test_skills_list(self, client: AsyncClient):
        """Skills endpoint returns list."""
        response = await client.get("/skills")
        assert response.status_code == 200
        data = response.json()
        # Returns {"skills": [...]}
        assert "skills" in data


class TestChannelsEndpoint:
    """Test channels listing endpoint."""

    async def test_channels_list(self, client: AsyncClient):
        """Channels endpoint returns channel info."""
        response = await client.get("/channels")
        assert response.status_code == 200
        data = response.json()
        # Returns {"channels": [...]}
        assert "channels" in data
