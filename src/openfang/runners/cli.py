"""CLI runner - thin wrapper around business logic."""

from __future__ import annotations

import asyncio
from pathlib import Path

import click
import httpx
import logfire

from openfang.agent import create_agent
from openfang.capabilities import InMemoryCron, InMemorySessions
from openfang.client import GatewayClient
from openfang.gateway import create_app
from openfang.models import User
from openfang.runners.cron import run_cron_with_agent
from openfang.runners.telegram import run_telegram_bot
from openfang.settings import settings


def run_async(coro):
    """Helper to run async functions."""
    return asyncio.run(coro)


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """OpenFang - AI agent gateway."""
    pass


# =============================================================================
# Chat commands - use pydantic-ai directly
# =============================================================================


def _make_cli_deps():
    """Create deps for CLI commands."""
    from openfang.deps import CommsAdapters, Deps, SchedulingAdapters, StorageAdapters, WebAdapters, WorkspaceAdapters

    root = Path.cwd()
    user = User(
        id=0,
        email=settings.user_email,
        roles={"admin"},
        phone=settings.user_phone,
        telegram_id=settings.user_telegram,
    )
    return Deps(
        user=user,
        storage=StorageAdapters.default(root),
        web_adapters=WebAdapters.default(),
        workspace=WorkspaceAdapters.default(root),
        scheduling=SchedulingAdapters.default(),
        comms=CommsAdapters.default(),
    )


@cli.command("chat")
def chat_cmd():
    """Interactive chat with the agent."""
    agent = create_agent()
    deps = _make_cli_deps()
    run_async(agent.to_cli(deps=deps, prog_name="openfang"))


@cli.command()
@click.argument("prompt")
def run(prompt: str):
    """Run a single prompt."""
    agent = create_agent()
    deps = _make_cli_deps()
    result = agent.run_sync(prompt, deps=deps)
    click.echo(result.output)


# =============================================================================
# Gateway commands
# =============================================================================


@cli.command()
@click.option("--host", default=None, help="Bind address")
@click.option("--port", default=None, type=int, help="Port")
@click.option("--logfire/--no-logfire", "use_logfire", default=None, help="Enable logfire")
def gateway(host: str | None, port: int | None, use_logfire: bool | None):
    """Run the OpenFang gateway HTTP server."""
    host = host or settings.host
    port = port or settings.port
    use_logfire = use_logfire if use_logfire is not None else settings.logfire_enabled

    if use_logfire:
        logfire.configure(service_name=settings.logfire_service_name, send_to_logfire=False)
        logfire.instrument_pydantic_ai()

    click.echo(f"Starting gateway on http://{host}:{port}")

    async def _run():
        import uvicorn

        app = create_app()
        config = uvicorn.Config(app, host=host, port=port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()

    run_async(_run())


@cli.command()
@click.option("--url", default="http://localhost:18789", help="Gateway URL")
def health(url: str):
    """Check gateway health."""
    client = GatewayClient(url)
    try:
        data = client.health()
        status = data.get("status", "unknown")
        if status == "healthy":
            click.secho(f"✓ Gateway healthy at {url}", fg="green")
            if "uptime" in data:
                click.echo(f"  Uptime: {data['uptime']}")
        else:
            click.secho(f"✗ Gateway unhealthy: {status}", fg="red")
    except httpx.ConnectError:
        click.secho(f"✗ Cannot connect to {url}", fg="red")
        raise SystemExit(1)


@cli.command()
@click.option("--url", default="http://localhost:18789", help="Gateway URL")
def status(url: str):
    """Show gateway status and configuration."""
    client = GatewayClient(url)

    click.echo("OpenFang Status")
    click.echo("=" * 40)

    if not client.is_running():
        click.secho("Gateway: not running", fg="yellow")
        click.echo("\nStart with: openfang gateway")
        return

    click.secho(f"Gateway: running at {url}", fg="green")
    click.echo("\nSettings:")
    click.echo(f"  Host: {settings.host}")
    click.echo(f"  Port: {settings.port}")
    click.echo(f"  Telegram: {'configured' if settings.telegram_bot_token else 'not configured'}")
    click.echo(f"  Discord: {'configured' if settings.discord_bot_token else 'not configured'}")

    try:
        skills = client.skills()
        eligible = [s for s in skills if s.get("eligible")]
        click.echo(f"\nSkills: {len(eligible)} available")
    except Exception:  # noqa: BLE001  # nosec B110
        pass  # Skills display is optional, don't fail status check


# =============================================================================
# Channel commands
# =============================================================================


@cli.command()
@click.option("-t", "--token", envvar="TELEGRAM_BOT_TOKEN", default=None)
def telegram(token: str | None):
    """Run Telegram bot listener."""
    token = token or settings.telegram_bot_token
    if not token:
        raise click.UsageError("Bot token required")
    click.echo("Starting Telegram bot...")
    run_async(run_telegram_bot(token))


@cli.command()
@click.option("-i", "--interval", default=60, help="Check interval (seconds)")
def cron(interval: int):
    """Run cron job checker."""
    click.echo(f"Starting cron checker (every {interval}s)...")

    async def _run():
        await run_cron_with_agent(InMemoryCron(), InMemorySessions(), check_interval=interval)

    run_async(_run())


@cli.group()
def message():
    """Send messages via channels."""
    pass


@message.command("send")
@click.argument("text")
@click.option("--to", "recipient", required=True, help="Recipient ID")
@click.option("--channel", default="telegram", help="Channel")
@click.option("--url", default="http://localhost:18789", help="Gateway URL")
def message_send(text: str, recipient: str, channel: str, url: str):
    """Send a message via a channel."""
    client = GatewayClient(url)
    try:
        client.send_message(channel, recipient, text)
        click.secho("✓ Message sent", fg="green")
    except httpx.ConnectError:
        click.secho(f"✗ Cannot connect to gateway at {url}", fg="red")
        raise SystemExit(1)
    except httpx.HTTPStatusError as e:
        click.secho(f"✗ Failed: {e.response.status_code}", fg="red")
        raise SystemExit(1)


# =============================================================================
# Config & diagnostics
# =============================================================================


@cli.command()
def skills():
    """List available skills."""
    from openfang.skills import SkillRegistry

    registry = SkillRegistry.default()
    eligible = registry.eligible_skills()

    click.echo("Available Skills")
    click.echo("=" * 40)

    for skill in eligible:
        emoji = skill.metadata.emoji or ""
        desc = skill.description[:50] if skill.description else ""
        click.echo(f"  {emoji} {skill.name} - {desc}...")


@cli.command()
def config():
    """Show current configuration."""

    click.echo("OpenFang Configuration")
    click.echo("=" * 40)
    click.echo(f"Model: {settings.get_model()}")
    click.echo(f"Host: {settings.host}")
    click.echo(f"Port: {settings.port}")
    click.echo(f"Telegram: {'✓' if settings.telegram_bot_token else '✗'}")
    click.echo(f"Discord: {'✓' if settings.discord_bot_token else '✗'}")


@cli.command()
@click.option("--fix", is_flag=True, help="Attempt to fix issues")
def doctor(fix: bool):
    """Run health checks and diagnose issues."""
    from openfang.doctor import Doctor

    report = Doctor().run_all()

    click.echo("OpenFang Doctor")
    click.echo("=" * 40)

    for check in report.checks:
        if check.ok:
            msg = f": {check.message}" if check.message else ""
            click.secho(f"✓ {check.name}{msg}", fg="green")
        else:
            click.secho(f"✗ {check.name}: {check.message}", fg="red")

    for warn in report.warnings:
        click.secho(f"! {warn.name}: {warn.message}", fg="yellow")

    click.echo()
    if report.issues:
        click.secho(f"Found {len(report.issues)} issue(s)", fg="red")
        raise SystemExit(1)
    else:
        click.secho("All checks passed!", fg="green")


@cli.command()
def onboard():
    """Interactive setup wizard."""
    import os

    click.echo("\n  OpenFang Setup\n")

    env_path = Path(".env")
    if env_path.exists() and not click.confirm(".env exists. Overwrite?", default=False):
        return

    provider = click.prompt("LLM provider", type=click.Choice(["openai", "anthropic"]), default="openai")
    key_name = "OPENAI_API_KEY" if provider == "openai" else "ANTHROPIC_API_KEY"
    existing = os.environ.get(key_name, "")

    if existing:
        click.echo(f"  {key_name} already set")
        api_key = existing
    else:
        api_key = click.prompt(key_name, hide_input=True)

    lines = ["# OpenFang", f"{key_name}={api_key}"]

    if click.confirm("Configure Telegram?", default=False):
        lines.append(f"OPENFANG_TELEGRAM_BOT_TOKEN={click.prompt('Token', hide_input=True)}")

    if click.confirm("Configure Discord?", default=False):
        lines.append(f"OPENFANG_DISCORD_BOT_TOKEN={click.prompt('Token', hide_input=True)}")

    env_path.write_text("\n".join(lines) + "\n")
    click.secho(f"✓ Wrote {env_path}", fg="green")


def main():
    cli()


if __name__ == "__main__":
    main()
