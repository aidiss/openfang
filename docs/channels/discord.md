# Discord

Status: **Production ready** — discord.py with slash commands and DM support.

## Quick Setup

### 1) Create a Discord Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **New Application** and give it a name
3. Go to **Bot** → Click **Add Bot**
4. Under **Token**, click **Copy** (or Reset Token if needed)

!!! warning "Privileged Intents"
    Enable **Message Content Intent** under Bot → Privileged Gateway Intents if you want the bot to read message content in servers.

### 2) Configure the Token

Add to your `.env` file:

```bash
OPENFANG_DISCORD_BOT_TOKEN=your-bot-token-here
```

### 3) Invite the Bot to Your Server

1. Go to **OAuth2** → **URL Generator**
2. Select scopes: `bot`, `applications.commands`
3. Select permissions: `Send Messages`, `Read Message History`
4. Copy the generated URL and open it
5. Select your server and authorize

### 4) Start the Gateway

```bash
uv run openfang gateway
```

You should see:

```
INFO: Discord channel started (account: default)
```

### 5) Chat with Your Bot

- **DM**: Send a direct message to your bot
- **Server**: Mention the bot or use slash commands

## Features

### Direct Messages

- Private session per user
- Full conversation context
- No server required

### Server Channels

- Mention the bot: `@YourBot what's the weather?`
- Each channel gets its own session
- Respects Discord permissions

### Slash Commands

Coming soon — `/ask`, `/remember`, `/forget`

## Configuration

```bash
# Required
OPENFANG_DISCORD_BOT_TOKEN=...
```

## Troubleshooting

### "Privileged intent not enabled"

Enable **Message Content Intent** in the Developer Portal:
Bot → Privileged Gateway Intents → Message Content Intent

### Bot doesn't respond in servers

1. Check bot has **Read Messages** and **Send Messages** permissions
2. Make sure you're mentioning the bot
3. Verify Message Content Intent is enabled

### "Invalid token"

Your token is wrong or was reset. Get a new one from the Developer Portal.

## See Also

- [Channels Overview](index.md)
- [Telegram Setup](telegram.md)
