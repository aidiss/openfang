"""CLI runner for the deps agent."""

from __future__ import annotations

import asyncio
from pathlib import Path

import click
import logfire

from openfang.capabilities import InMemoryConversations, InMemoryCron
from openfang.chat import chat, start_conversation
from openfang.deps import Deps, create_deps
from openfang.gateway import Gateway, HeartbeatConfig, serve
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
    """AI Agent with tools for files, web, cron, and telegram."""
    pass


@cli.command()
@click.option("-u", "--user", default="user@cli", help="User email")
@click.option("-r", "--role", multiple=True, default=["developer"], help="User roles (can repeat)")
@click.option("-p", "--project", type=click.Path(exists=True, path_type=Path), default=".", help="Project root")
@click.option("-c", "--conversation", default="cli-session", help="Conversation ID")
def chat_cmd(user: str, role: tuple[str], project: Path, conversation: str):
    """Interactive chat with the agent."""

    async def _run():
        usr = User(id=1, email=user, roles=set(role))
        conversations = InMemoryConversations()

        click.echo(f"Chat as {usr.email} (roles: {', '.join(usr.roles)})")
        click.echo(f"Project: {project.resolve()}")
        click.echo("Commands: quit, clear")
        click.echo("-" * 40)

        async with create_deps(user=usr, root=project, conversations=conversations) as deps:
            await deps.workspace.projects.register("current", project)
            await start_conversation(deps, conversation)

            while True:
                try:
                    text = click.prompt("\nYou", prompt_suffix=": ")
                except (KeyboardInterrupt, EOFError, click.Abort):
                    click.echo("\nBye!")
                    break

                if text.lower() in ("quit", "exit"):
                    break
                if text.lower() == "clear":
                    await deps.storage.conversations.delete(conversation)
                    await start_conversation(deps, conversation)
                    click.echo("Cleared.")
                    continue
                if not text.strip():
                    continue

                try:
                    response = await chat(deps, text)
                    click.echo(f"\nAgent: {response}")
                except Exception as e:
                    click.echo(f"\nError: {e}", err=True)

    run_async(_run())


@cli.command()
@click.argument("prompt")
@click.option("-u", "--user", default="user@cli", help="User email")
@click.option("-r", "--role", multiple=True, default=["developer"], help="User roles")
@click.option("-p", "--project", type=click.Path(exists=True, path_type=Path), default=".", help="Project root")
def run(prompt: str, user: str, role: tuple[str], project: Path):
    """Run a single prompt."""

    async def _run():
        usr = User(id=1, email=user, roles=set(role))

        async with create_deps(user=usr, root=project) as deps:
            await deps.workspace.projects.register("current", project)
            response = await chat(deps, prompt)
            click.echo(response)

    run_async(_run())


@cli.command()
@click.option(
    "-t", "--token", envvar="TELEGRAM_BOT_TOKEN", default=None, help="Bot token (or set OPENFANG_TELEGRAM_BOT_TOKEN)"
)
def telegram(token: str | None):
    """Run Telegram bot listener."""
    from ..settings import settings

    token = token or settings.telegram_bot_token
    if not token:
        raise click.UsageError("Bot token required: use --token, TELEGRAM_BOT_TOKEN, or OPENFANG_TELEGRAM_BOT_TOKEN")

    click.echo("Starting Telegram bot...")
    run_async(run_telegram_bot(token))


@cli.command()
@click.option("-i", "--interval", default=60, help="Check interval (seconds)")
def cron(interval: int):
    """Run cron job checker."""
    click.echo(f"Starting cron checker (every {interval}s)...")

    async def _run():
        cron_svc = InMemoryCron()
        conversations = InMemoryConversations()
        await run_cron_with_agent(cron_svc, conversations, check_interval=interval)

    run_async(_run())


def _parse_interval(value: str) -> int:
    """Parse interval like '30m', '1h', '90s' to seconds."""
    value = value.strip().lower()
    if value.endswith("s"):
        return int(value[:-1])
    if value.endswith("m"):
        return int(value[:-1]) * 60
    if value.endswith("h"):
        return int(value[:-1]) * 3600
    return int(value)


@cli.command()
@click.option("--host", default=None, help="Bind address (default from settings)")
@click.option("--port", default=None, type=int, help="Port (default from settings)")
@click.option("--heartbeat/--no-heartbeat", default=None, help="Enable heartbeat")
@click.option("--logfire/--no-logfire", "use_logfire", default=None, help="Enable logfire")
def gateway(host: str | None, port: int | None, heartbeat: bool | None, use_logfire: bool | None):
    """Run the OpenFang gateway HTTP server.

    Starts FastAPI server with heartbeat loop. API docs at /docs.
    Settings can be configured via OPENFANG_* env vars or .env file.
    """

    # Use settings with CLI overrides
    host = host or settings.host
    port = port or settings.port
    heartbeat = heartbeat if heartbeat is not None else settings.heartbeat_enabled
    use_logfire = use_logfire if use_logfire is not None else settings.logfire_enabled

    # Initialize logfire
    if use_logfire:
        logfire.configure(service_name=settings.logfire_service_name, send_to_logfire=False)
        logfire.instrument_pydantic_ai()
        click.echo("Logfire: enabled")

    hb_config = HeartbeatConfig(
        enabled=heartbeat,
        interval=settings.heartbeat_interval,
    )

    click.echo(f"Starting OpenFang gateway on http://{host}:{port}")
    click.echo(f"  API docs: http://{host}:{port}/docs")
    click.echo(f"  Heartbeat: {'enabled' if heartbeat else 'disabled'} ({settings.heartbeat_interval}s)")
    click.echo("-" * 40)

    async def _run():
        from ..chat import start_conversation
        from ..deps import CommsAdapters, SchedulingAdapters, StorageAdapters, WebAdapters, WorkspaceAdapters

        user = User(id=0, email="gateway@system", roles={"admin"})
        root = Path.cwd()
        deps = Deps(
            user=user,
            storage=StorageAdapters.default(root),
            web_adapters=WebAdapters.default(),
            workspace=WorkspaceAdapters.default(root),
            scheduling=SchedulingAdapters.default(),
            comms=CommsAdapters.default(),
        )
        await start_conversation(deps, "web-session")
        gw = Gateway(deps=deps, heartbeat=hb_config)
        await serve(gw, host=host, port=port)

    run_async(_run())


@cli.command()
@click.option("--url", default="http://localhost:18789", help="Gateway URL")
def health(url: str):
    """Check gateway health."""
    import httpx

    try:
        resp = httpx.get(f"{url}/health", timeout=5)
        data = resp.json()
        status = data.get("status", "unknown")
        if status == "healthy":
            click.secho(f"✓ Gateway healthy at {url}", fg="green")
            if "uptime" in data:
                click.echo(f"  Uptime: {data['uptime']}")
            if "channels" in data:
                click.echo(f"  Channels: {data['channels']}")
        else:
            click.secho(f"✗ Gateway unhealthy: {status}", fg="red")
    except httpx.ConnectError:
        click.secho(f"✗ Cannot connect to {url}", fg="red")
        click.echo("  Is the gateway running? Try: openfang gateway")
        raise SystemExit(1)
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red")
        raise SystemExit(1)


@cli.command()
@click.option("--url", default="http://localhost:18789", help="Gateway URL")
def status(url: str):
    """Show gateway status and configuration."""
    import httpx

    click.echo("OpenFang Status")
    click.echo("=" * 40)

    # Check gateway
    try:
        resp = httpx.get(f"{url}/health", timeout=5)
        data = resp.json()
        click.secho(f"Gateway: running at {url}", fg="green")
    except httpx.ConnectError:
        click.secho("Gateway: not running", fg="yellow")
        click.echo("\nStart with: openfang gateway")
        return

    # Show settings
    click.echo(f"\nSettings:")
    click.echo(f"  Host: {settings.host}")
    click.echo(f"  Port: {settings.port}")
    click.echo(f"  Telegram: {'configured' if settings.telegram_bot_token else 'not configured'}")
    click.echo(f"  Discord: {'configured' if settings.discord_bot_token else 'not configured'}")

    # Show skills
    try:
        resp = httpx.get(f"{url}/skills", timeout=5)
        skills = resp.json()
        eligible = [s for s in skills if s.get("eligible")]
        click.echo(f"\nSkills: {len(eligible)} available")
        for skill in eligible[:5]:
            click.echo(f"  • {skill.get('name', 'unknown')}")
        if len(eligible) > 5:
            click.echo(f"  ... and {len(eligible) - 5} more")
    except Exception:
        pass


@cli.command()
def skills():
    """List available skills."""
    from ..skills import SkillRegistry

    registry = SkillRegistry.default()
    eligible = registry.eligible_skills()
    unavailable = [s for s in registry.skills.values() if s not in eligible]

    click.echo("Available Skills")
    click.echo("=" * 40)

    if eligible:
        click.secho("✓ Eligible:", fg="green")
        for skill in eligible:
            emoji = skill.metadata.emoji or ""
            desc = skill.description[:50] if skill.description else ""
            click.echo(f"  {emoji} {skill.name} - {desc}...")
    else:
        click.echo("  (none)")

    if unavailable:
        click.secho("\n✗ Unavailable (missing requirements):", fg="yellow")
        for skill in unavailable:
            reqs = skill.metadata.requires
            missing = []
            if reqs.bins:
                missing.append(f"bins: {', '.join(reqs.bins)}")
            if reqs.env:
                missing.append(f"env: {', '.join(reqs.env)}")
            if missing:
                click.echo(f"  {skill.name} (needs {'; '.join(missing)})")
            else:
                click.echo(f"  {skill.name}")


@cli.command()
def config():
    """Show current configuration."""
    click.echo("OpenFang Configuration")
    click.echo("=" * 40)
    click.echo(f"Host: {settings.host}")
    click.echo(f"Port: {settings.port}")
    click.echo(f"Heartbeat: {'enabled' if settings.heartbeat_enabled else 'disabled'} ({settings.heartbeat_interval}s)")
    click.echo(f"Logfire: {'enabled' if settings.logfire_enabled else 'disabled'}")
    click.echo()
    click.echo("Channels:")
    click.echo(f"  Telegram: {'✓ configured' if settings.telegram_bot_token else '✗ not set'}")
    click.echo(f"  Discord: {'✓ configured' if settings.discord_bot_token else '✗ not set'}")
    click.echo()
    click.echo("Environment variables:")
    click.echo("  OPENFANG_HOST, OPENFANG_PORT")
    click.echo("  OPENFANG_TELEGRAM_BOT_TOKEN")
    click.echo("  OPENFANG_DISCORD_BOT_TOKEN")
    click.echo("  OPENAI_API_KEY or ANTHROPIC_API_KEY")


def main():
    cli()


if __name__ == "__main__":
    main()
