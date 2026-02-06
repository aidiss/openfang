"""Gateway HTTP client for CLI commands."""

from __future__ import annotations

from dataclasses import dataclass

import httpx


@dataclass
class GatewayClient:
    """HTTP client for OpenFang gateway."""

    url: str = "http://localhost:18789"
    timeout: float = 10.0

    def health(self) -> dict:
        """Get gateway health status."""
        resp = httpx.get(f"{self.url}/health", timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def skills(self) -> list[dict]:
        """Get list of skills."""
        resp = httpx.get(f"{self.url}/skills", timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def send_message(self, channel: str, to: str, text: str) -> dict:
        """Send a message via a channel."""
        resp = httpx.post(
            f"{self.url}/api/messages",
            json={"channel": channel, "to": to, "text": text},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def is_running(self) -> bool:
        """Check if gateway is running."""
        try:
            self.health()
            return True
        except httpx.ConnectError:
            return False
