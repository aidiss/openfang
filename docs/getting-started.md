# Getting Started

Goal: go from **zero** → **first working chat** in under 5 minutes.

## Installation

=== "One-liner"

    ```bash
    # Works everywhere. Installs uv if needed. 🐍
    curl -fsSL https://openfang.ai/install.sh | bash
    ```

    This installs to `~/openfang` and adds `openfang` to your PATH:

    ```bash
    openfang chat      # Just works
    openfang gateway   # Web UI at localhost:18789
    ```

    Customize install location with `OPENFANG_DIR`:

    ```bash
    curl -fsSL https://openfang.ai/install.sh | OPENFANG_DIR=~/my-agent bash
    ```

=== "uvx"

    ```bash
    # Try it without installing (requires uv)
    uvx openfang chat
    ```

    Or install permanently:

    ```bash
    uv tool install openfang
    openfang chat
    ```

    !!! warning "Coming Soon"
        PyPI publishing is in progress. Use the one-liner or hackable method for now.

=== "Hackable"

    ```bash
    # Clone and own it
    git clone https://github.com/aidiss/openfang.git
    cd openfang
    uv sync
    ```

    In dev mode, use `uv run`:

    ```bash
    uv run openfang chat
    ```

    This is the recommended method if you want to modify the code or contribute.

## Prerequisites

- **Python 3.13+** (the one-liner handles this)
- An LLM API key (OpenAI or Anthropic)

## Configure Environment

Create a `.env` file (or edit the one created by the installer):

```bash
# Required: LLM provider (pick one)
OPENAI_API_KEY=sk-...
# Or: ANTHROPIC_API_KEY=sk-ant-...

# Optional: Enable channels
OPENFANG_TELEGRAM_BOT_TOKEN=123456:ABC...
OPENFANG_DISCORD_BOT_TOKEN=...
```

## Start the Gateway

```bash
uv run openfang gateway
```

Open [localhost:18789](http://localhost:18789) in your browser. You'll see the dashboard with:

- **Chat** — Direct conversation with the agent
- **Sessions** — View conversation history
- **Channels** — Connected messaging platforms
- **Skills** — Available agent capabilities
- **Memory** — Persistent facts the agent remembers

## Send Your First Message

Type in the chat input:

> What can you help me with?

The agent will respond with its capabilities based on enabled tools and skills.

## Quick Alternative: CLI Chat

Don't need the web UI? Chat directly in your terminal:

```bash
uv run openfang chat
```

## Next Steps

<div class="grid cards" markdown>

-   :material-telegram: **[Connect Telegram](channels/telegram.md)**

    ---

    Set up a Telegram bot for mobile access

-   :material-puzzle: **[Add Skills](skills.md)**

    ---

    Extend capabilities with markdown skills

-   :material-cog: **[Architecture](architecture.md)**

    ---

    Understand how OpenFang works

</div>

## CLI Commands

```bash
openfang --help        # Show all commands
openfang config        # Show current configuration
openfang skills        # List available skills
openfang health        # Check if gateway is running
openfang status        # Full status check

openfang gateway       # Start the gateway server
openfang chat          # Interactive terminal chat
openfang run "prompt"  # Single prompt, get response
openfang telegram      # Run Telegram bot standalone
```

## Troubleshooting

### "No API key found"

Make sure your `.env` file is in the project root and contains a valid API key:

```bash
cat .env  # Should show OPENAI_API_KEY or ANTHROPIC_API_KEY
```

### Port already in use

Change the port:

```bash
OPENFANG_PORT=8080 uv run openfang gateway
```

### Gateway won't start

Check Python version:

```bash
python --version  # Should be 3.13+
```

Run with verbose logging:

```bash
uv run openfang gateway --verbose
```
