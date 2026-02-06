"""E2E test fixtures.

Provides two testing approaches:
1. Fast API tests via httpx.AsyncClient (no server needed)
2. Browser tests via Playwright (requires live server)
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

import pytest
from httpx import ASGITransport, AsyncClient

from openfang.capabilities import (
    InMemoryConversations,
    InMemoryCron,
    InMemoryMemory,
    LocalFiles,
    LocalProjects,
    LocalShell,
    PlaywrightWeb,
)
from openfang.channels import ChannelRegistry
from openfang.deps import (
    CommsAdapters,
    Deps,
    SchedulingAdapters,
    StorageAdapters,
    WebAdapters,
    WorkspaceAdapters,
)
from openfang.gateway.app import app, init_app
from openfang.gateway.core import Gateway
from openfang.models import User
from openfang.skills import SkillRegistry

if TYPE_CHECKING:
    from pathlib import Path


# =============================================================================
# Core fixtures
# =============================================================================


@pytest.fixture
def e2e_user() -> User:
    """Admin user for E2E tests with full permissions."""
    return User(id=1, email="e2e@test.com", roles={"admin"})


@pytest.fixture
def e2e_deps(e2e_user: User, tmp_path: Path) -> Deps:
    """Deps with all InMemory adapters for E2E tests."""
    return Deps(
        user=e2e_user,
        conversation_id="e2e-session",
        storage=StorageAdapters(
            files=LocalFiles(root=tmp_path),
            memory=InMemoryMemory(),
            conversations=InMemoryConversations(),
        ),
        web_adapters=WebAdapters(web=PlaywrightWeb()),
        workspace=WorkspaceAdapters(
            shell=LocalShell(tmp_path),
            projects=LocalProjects(),
        ),
        scheduling=SchedulingAdapters(cron=InMemoryCron()),
        comms=CommsAdapters(
            channels=ChannelRegistry(),
            skills=SkillRegistry(),
        ),
    )


@pytest.fixture
def e2e_gateway(e2e_deps: Deps) -> Gateway:
    """Gateway with test deps, app initialized."""
    gw = Gateway(deps=e2e_deps)
    init_app(gw)
    return gw


# =============================================================================
# Fast API testing (no server)
# =============================================================================


@pytest.fixture
async def client(e2e_gateway: Gateway) -> AsyncIterator[AsyncClient]:
    """Fast API client via ASGITransport - no server needed."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


# =============================================================================
# Browser testing (requires live server)
# =============================================================================


@pytest.fixture
async def live_server(e2e_gateway: Gateway) -> AsyncIterator[str]:
    """Run gateway on random port for browser tests."""
    import socket

    import uvicorn

    # Find available port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]

    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)
    task = asyncio.create_task(server.serve())

    # Wait for server to start
    await asyncio.sleep(0.3)

    yield f"http://127.0.0.1:{port}"

    # Cleanup
    server.should_exit = True
    await task
