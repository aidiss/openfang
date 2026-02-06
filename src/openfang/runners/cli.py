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


def main():
    cli()


if __name__ == "__main__":
    main()
