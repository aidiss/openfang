"""Health checks and diagnostics for OpenFang."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

import httpx

from openfang.settings import settings


@dataclass
class CheckResult:
    """Result of a single health check."""

    name: str
    ok: bool
    message: str = ""
    fix_hint: str | None = None


@dataclass
class DoctorReport:
    """Aggregated doctor report."""

    checks: list[CheckResult] = field(default_factory=list)
    warnings: list[CheckResult] = field(default_factory=list)

    @property
    def issues(self) -> list[CheckResult]:
        return [c for c in self.checks if not c.ok]

    @property
    def passed(self) -> bool:
        return len(self.issues) == 0


class Doctor:
    """Health checker for OpenFang installation."""

    def __init__(self, root: Path | None = None):
        self.root = root or Path.cwd()
        self.report = DoctorReport()

    def check(self, name: str, ok: bool, message: str = "", fix_hint: str | None = None) -> bool:
        """Record a check result."""
        self.report.checks.append(CheckResult(name, ok, message, fix_hint))
        return ok

    def warn(self, name: str, message: str) -> None:
        """Record a warning (not a failure)."""
        self.report.warnings.append(CheckResult(name, True, message))

    def check_python_version(self) -> bool:
        """Check Python version is 3.13+."""
        v = sys.version_info
        ok = v >= (3, 13)
        return self.check(
            "Python version",
            ok,
            "" if ok else f"Python 3.13+ required, got {v.major}.{v.minor}",
            None if ok else "Install Python 3.13+: https://www.python.org/downloads/",
        )

    def check_env_file(self) -> bool:
        """Check .env file exists."""
        env_path = self.root / ".env"
        if env_path.exists():
            return self.check(".env file", True)
        self.warn(".env file", "Not found (optional but recommended)")
        return True

    def check_api_key(self) -> str | None:
        """Check API key is configured. Returns provider name if found."""
        gateway_key = os.environ.get("PYDANTIC_AI_GATEWAY_API_KEY")
        openai_key = os.environ.get("OPENAI_API_KEY")
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

        if gateway_key:
            self.check("API key", True, "Pydantic AI Gateway configured")
            return "gateway"
        if openai_key:
            self.check("API key", True, "OpenAI configured")
            return "openai"
        if anthropic_key:
            self.check("API key", True, "Anthropic configured")
            return "anthropic"

        self.check(
            "API key",
            False,
            "No API key found",
            "Set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env",
        )
        return None

    def check_pydantic_gateway(self) -> bool:
        """Check if pydantic-ai gateway is configured and reachable."""
        gateway_key = os.environ.get("PYDANTIC_AI_GATEWAY_API_KEY")
        if not gateway_key:
            self.warn("Pydantic AI Gateway", "Not configured (set PYDANTIC_AI_GATEWAY_API_KEY to enable)")
            return True

        gateway_url = os.environ.get("PYDANTIC_AI_GATEWAY_URL", "https://gateway.pydantic.dev")

        try:
            # Try to verify the gateway is reachable
            resp = httpx.get(
                f"{gateway_url}/health",
                headers={"Authorization": f"Bearer {gateway_key}"},
                timeout=5,
            )
            if resp.status_code == 200:
                return self.check("Pydantic AI Gateway", True, f"Connected to {gateway_url}")
            # Some gateways may not have /health, try root
            if resp.status_code == 404:
                return self.check("Pydantic AI Gateway", True, f"Configured ({gateway_url})")
            return self.check(
                "Pydantic AI Gateway",
                False,
                f"Gateway returned {resp.status_code}",
                "Check PYDANTIC_AI_GATEWAY_API_KEY and PYDANTIC_AI_GATEWAY_URL",
            )
        except httpx.RequestError as e:
            self.warn("Pydantic AI Gateway", f"Could not verify connectivity: {e}")
            return True

    def check_openai_key_valid(self) -> bool:
        """Verify OpenAI API key works."""
        key = os.environ.get("OPENAI_API_KEY")
        if not key or os.environ.get("PYDANTIC_AI_GATEWAY_API_KEY"):
            return True  # Skip if no key or using gateway

        try:
            resp = httpx.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {key}"},
                timeout=5,
            )
            ok = resp.status_code == 200
            return self.check(
                "OpenAI API key valid",
                ok,
                "" if ok else f"API returned {resp.status_code}",
            )
        except httpx.RequestError as e:
            self.warn("OpenAI API", f"Could not verify: {e}")
            return True

    def check_gateway(self) -> bool:
        """Check if gateway is running."""
        url = f"http://{settings.host}:{settings.port}"
        try:
            resp = httpx.get(f"{url}/health", timeout=2)
            if resp.status_code == 200:
                return self.check("Gateway", True, f"Running at {url}")
            self.warn("Gateway", f"Responded with {resp.status_code}")
            return True
        except httpx.ConnectError:
            self.warn("Gateway", f"Not running at {url} (start with: openfang gateway)")
            return True

    def check_telegram(self) -> bool:
        """Check Telegram bot token if configured."""
        token = settings.telegram_bot_token
        if not token:
            return True

        try:
            resp = httpx.get(f"https://api.telegram.org/bot{token}/getMe", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                bot_name = data.get("result", {}).get("username", "unknown")
                return self.check("Telegram bot", True, f"@{bot_name}")
            return self.check(
                "Telegram token",
                False,
                "Invalid token",
                "Check OPENFANG_TELEGRAM_BOT_TOKEN",
            )
        except httpx.RequestError as e:
            self.warn("Telegram", f"Could not verify: {e}")
            return True

    def check_discord(self) -> bool:
        """Check Discord bot token if configured."""
        token = settings.discord_bot_token
        if not token:
            return True

        try:
            resp = httpx.get(
                "https://discord.com/api/v10/users/@me",
                headers={"Authorization": f"Bot {token}"},
                timeout=5,
            )
            if resp.status_code == 200:
                data = resp.json()
                bot_name = data.get("username", "unknown")
                return self.check("Discord bot", True, bot_name)
            return self.check(
                "Discord token",
                False,
                "Invalid token",
                "Check OPENFANG_DISCORD_BOT_TOKEN",
            )
        except httpx.RequestError as e:
            self.warn("Discord", f"Could not verify: {e}")
            return True

    def check_skills(self) -> bool:
        """Check skills are loadable."""
        from openfang.skills import SkillRegistry

        try:
            registry = SkillRegistry.default()
            eligible = registry.eligible_skills()
            return self.check("Skills", True, f"{len(eligible)} available")
        except Exception as e:
            return self.check("Skills", False, str(e))

    def run_all(self) -> DoctorReport:
        """Run all health checks."""
        self.check_python_version()
        self.check_env_file()
        self.check_api_key()
        self.check_pydantic_gateway()
        self.check_openai_key_valid()
        self.check_gateway()
        self.check_telegram()
        self.check_discord()
        self.check_skills()
        return self.report
