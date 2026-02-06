# Getting Started

Goal: go from **zero** → **first working chat** in under 5 minutes.

## Prerequisites

- **Python 3.13+**
- **uv** (recommended) or pip
- An LLM API key (OpenAI or Anthropic)

## 1) Clone and Install

```bash
git clone https://github.com/aidiss/openfang.git
cd openfang

# Install dependencies
uv sync
```

## 2) Configure Environment

Create a `.env` file:

```bash
# Required: LLM provider (pick one)
OPENAI_API_KEY=sk-...
# Or: ANTHROPIC_API_KEY=sk-ant-...

# Optional: Enable channels
OPENFANG_TELEGRAM_BOT_TOKEN=123456:ABC...
OPENFANG_DISCORD_BOT_TOKEN=...
```

## 3) Start the Gateway

```bash
uv run openfang gateway
```

Open [localhost:18789](http://localhost:18789) in your browser. You'll see the dashboard with:

- **Chat** — Direct conversation with the agent
- **Sessions** — View conversation history
- **Channels** — Connected messaging platforms
- **Skills** — Available agent capabilities
- **Memory** — Persistent facts the agent remembers

## 4) Send Your First Message

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
