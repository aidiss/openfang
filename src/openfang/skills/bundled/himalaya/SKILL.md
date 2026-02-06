---
name: himalaya
description: "CLI email client via IMAP/SMTP. List, read, write, reply, and organize emails."
homepage: https://github.com/pimalaya/himalaya
metadata:
  {
    "openfang":
      {
        "emoji": "📧",
        "requires": { "bins": ["himalaya"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "himalaya",
              "bins": ["himalaya"],
              "label": "Install Himalaya (brew)",
            },
          ],
      },
  }
---

# Himalaya Email CLI

Himalaya is a terminal email client using IMAP/SMTP backends.

## Prerequisites

1. Himalaya installed (`himalaya --version`)
2. Config at `~/.config/himalaya/config.toml`
3. IMAP/SMTP credentials configured

## Quick Setup

Run the wizard:

```bash
himalaya account configure
```

Or create `~/.config/himalaya/config.toml`:

```toml
[accounts.personal]
email = "you@example.com"
display-name = "Your Name"
default = true

backend.type = "imap"
backend.host = "imap.example.com"
backend.port = 993
backend.encryption.type = "tls"
backend.login = "you@example.com"
backend.auth.type = "password"
backend.auth.cmd = "pass show email/imap"

message.send.backend.type = "smtp"
message.send.backend.host = "smtp.example.com"
message.send.backend.port = 587
message.send.backend.encryption.type = "start-tls"
message.send.backend.login = "you@example.com"
message.send.backend.auth.type = "password"
message.send.backend.auth.cmd = "pass show email/smtp"
```

## Common Operations

### List & Read

```bash
# List folders
himalaya folder list

# List emails in INBOX
himalaya envelope list

# List emails in folder
himalaya envelope list --folder "Sent"

# Search emails
himalaya envelope list from john@example.com subject meeting

# Read email by ID
himalaya message read 42
```

### Write & Reply

```bash
# Interactive compose
himalaya message write

# Send directly
cat << 'EOF' | himalaya template send
From: you@example.com
To: recipient@example.com
Subject: Test

Hello from Himalaya!
EOF

# Reply to email
himalaya message reply 42

# Reply-all
himalaya message reply 42 --all

# Forward
himalaya message forward 42
```

### Organize

```bash
# Move to folder
himalaya message move 42 "Archive"

# Copy to folder
himalaya message copy 42 "Important"

# Delete
himalaya message delete 42

# Mark as read
himalaya flag add 42 --flag seen

# Mark as unread
himalaya flag remove 42 --flag seen
```

### Multiple Accounts

```bash
# List accounts
himalaya account list

# Use specific account
himalaya --account work envelope list
```

### Attachments

```bash
# Download attachments
himalaya attachment download 42

# Save to directory
himalaya attachment download 42 --dir ~/Downloads
```

## JSON Output

```bash
himalaya envelope list --output json
```
