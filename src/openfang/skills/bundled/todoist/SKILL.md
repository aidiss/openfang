---
name: todoist
description: Manage Todoist tasks, projects, and labels via REST API.
homepage: https://developer.todoist.com/rest/v2
metadata:
  {
    "openfang":
      {
        "emoji": "✅",
        "requires": { "bins": ["curl", "jq"], "env": ["TODOIST_API_TOKEN"] },
        "primaryEnv": "TODOIST_API_TOKEN",
      },
  }
---

# Todoist

Manage tasks, projects, and labels via Todoist REST API.

## Setup

1. Go to Settings → Integrations → Developer
2. Copy your API token
3. Set environment variable:

```bash
export TODOIST_API_TOKEN="your_token_here"
```

## Tasks

### List Active Tasks

```bash
curl -s "https://api.todoist.com/rest/v2/tasks" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" | jq '.[] | {id, content, due: .due.date, priority, project_id}'
```

### List Tasks in Project

```bash
curl -s "https://api.todoist.com/rest/v2/tasks?project_id=PROJECT_ID" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" | jq
```

### Get Task

```bash
curl -s "https://api.todoist.com/rest/v2/tasks/TASK_ID" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" | jq
```

### Create Task

```bash
curl -s -X POST "https://api.todoist.com/rest/v2/tasks" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Buy groceries",
    "due_string": "tomorrow at 10am",
    "priority": 4
  }' | jq
```

With project and labels:

```bash
curl -s -X POST "https://api.todoist.com/rest/v2/tasks" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Review PR",
    "project_id": "PROJECT_ID",
    "labels": ["work", "urgent"],
    "due_string": "today",
    "priority": 3
  }' | jq
```

### Update Task

```bash
curl -s -X POST "https://api.todoist.com/rest/v2/tasks/TASK_ID" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Updated task name", "priority": 2}' | jq
```

### Complete Task

```bash
curl -s -X POST "https://api.todoist.com/rest/v2/tasks/TASK_ID/close" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN"
```

### Reopen Task

```bash
curl -s -X POST "https://api.todoist.com/rest/v2/tasks/TASK_ID/reopen" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN"
```

### Delete Task

```bash
curl -s -X DELETE "https://api.todoist.com/rest/v2/tasks/TASK_ID" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN"
```

## Projects

### List Projects

```bash
curl -s "https://api.todoist.com/rest/v2/projects" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" | jq '.[] | {id, name, color}'
```

### Create Project

```bash
curl -s -X POST "https://api.todoist.com/rest/v2/projects" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Project", "color": "blue"}' | jq
```

## Labels

### List Labels

```bash
curl -s "https://api.todoist.com/rest/v2/labels" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" | jq '.[] | {id, name, color}'
```

### Create Label

```bash
curl -s -X POST "https://api.todoist.com/rest/v2/labels" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "urgent", "color": "red"}' | jq
```

## Due Dates

Todoist supports natural language for `due_string`:

- `today`, `tomorrow`, `next monday`
- `every day at 9am`
- `every weekday`
- `in 3 days`
- `Jan 15 at 2pm`

## Priority

- `1` = Normal (no priority)
- `2` = Low (blue)
- `3` = Medium (orange)
- `4` = High (red/urgent)

## Tips

- Task `content` supports Markdown
- Use labels for filtering and organization
- `due_string` is parsed naturally; `due_date` for exact ISO dates
- Rate limit: 450 requests per 15 minutes
