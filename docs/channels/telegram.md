# Telegram

Status: **Production ready** — Bot API via python-telegram-bot with long-polling.

## Quick Setup

### 1) Create a Bot with @BotFather

1. Open Telegram and chat with **[@BotFather](https://t.me/BotFather)**
2. Send `/newbot`
3. Follow prompts: choose a name and username (must end in `bot`)
4. Copy the token (looks like `123456789:ABCdef...`)

!!! tip "Keep your token secret"
    Never commit tokens to git. Use environment variables or `.env` files.

### 2) Configure the Token

Add to your `.env` file:

```bash
OPENFANG_TELEGRAM_BOT_TOKEN=123456789:ABCdef-your-token-here
```

Or set via environment:

```bash
export OPENFANG_TELEGRAM_BOT_TOKEN=123456789:ABCdef...
```

### 3) Start the Gateway

```bash
uv run openfang gateway
```

You should see:

```
INFO: Telegram channel started (account: default)
```

### 4) Chat with Your Bot

Find your bot on Telegram (by the username you chose) and send a message!

## Features

### Direct Messages

- DMs create a private session per user
- Full conversation history maintained
- All tools available (based on permissions)

### Groups

- Add the bot to a group
- Mention the bot (`@yourbot`) to trigger responses
- Group sessions are isolated from DMs

### Supported Content

| Type | Receive | Send |
|------|---------|------|
| Text | ✅ | ✅ |
| Images | 🔜 | 🔜 |
| Files | 🔜 | 🔜 |
| Voice | 🔜 | 🔜 |

## Configuration Options

Full settings available via environment:

```bash
# Required
OPENFANG_TELEGRAM_BOT_TOKEN=...

# Optional: custom polling interval (seconds)
# OPENFANG_TELEGRAM_POLL_INTERVAL=1
```

## Troubleshooting

### "Unauthorized" error

Your token is invalid or expired. Get a new one from @BotFather.

### Bot doesn't respond

1. Check the gateway logs for errors
2. Verify the token is set correctly
3. Make sure the gateway is running

### "Conflict: terminated by other getUpdates"

Another instance is polling with the same token. Stop other instances or use webhooks (coming soon).

## Architecture

```
Telegram Cloud
      │
      │ Long-polling (getUpdates)
      ▼
┌─────────────────┐
│ TelegramChannel │
│  (python-tg-bot)│
└────────┬────────┘
         │
         ▼
   InboundMessage
         │
         ▼
    Dispatcher
         │
         ▼
      Agent
         │
         ▼
   OutboundMessage
         │
         ▼
┌─────────────────┐
│ TelegramChannel │
│   send_message  │
└────────┬────────┘
         │
         ▼
   Telegram Cloud
```

## See Also

- [Channels Overview](index.md)
- [Discord Setup](discord.md)
