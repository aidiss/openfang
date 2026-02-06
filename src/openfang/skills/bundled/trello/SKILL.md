---
name: trello
description: Manage Trello boards, lists, and cards via REST API.
homepage: https://developer.atlassian.com/cloud/trello/rest/
metadata:
  {
    "openfang":
      {
        "emoji": "📋",
        "requires": { "bins": ["curl", "jq"], "env": ["TRELLO_API_KEY", "TRELLO_TOKEN"] },
        "primaryEnv": "TRELLO_API_KEY",
      },
  }
---

# Trello

Manage Trello boards, lists, and cards via the REST API.

## Setup

1. Get API key: https://trello.com/app-key
2. Generate token (click "Token" link on that page)
3. Set environment variables:

```bash
export TRELLO_API_KEY="your-api-key"  # pragma: allowlist secret
export TRELLO_TOKEN="your-token"  # pragma: allowlist secret
```

## Boards

List all boards:

```bash
curl -s "https://api.trello.com/1/members/me/boards?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq '.[] | {name, id}'
```

Find board by name:

```bash
curl -s "https://api.trello.com/1/members/me/boards?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq '.[] | select(.name | contains("Work"))'
```

## Lists

List all lists in a board:

```bash
curl -s "https://api.trello.com/1/boards/{boardId}/lists?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq '.[] | {name, id}'
```

## Cards

List cards in a list:

```bash
curl -s "https://api.trello.com/1/lists/{listId}/cards?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq '.[] | {name, id, desc}'
```

Create a card:

```bash
curl -s -X POST "https://api.trello.com/1/cards?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -d "idList={listId}" \
  -d "name=Card Title" \
  -d "desc=Card description"
```

Move card to another list:

```bash
curl -s -X PUT "https://api.trello.com/1/cards/{cardId}?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -d "idList={newListId}"
```

Add comment:

```bash
curl -s -X POST "https://api.trello.com/1/cards/{cardId}/actions/comments?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -d "text=Your comment here"
```

Archive card:

```bash
curl -s -X PUT "https://api.trello.com/1/cards/{cardId}?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -d "closed=true"
```

## Notes

- IDs can be found in Trello URLs or via list commands
- Rate limits: 300 req/10s per API key, 100 req/10s per token
