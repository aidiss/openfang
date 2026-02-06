---
name: linear
description: Manage Linear issues, projects, and cycles via GraphQL API.
homepage: https://developers.linear.app/docs
metadata:
  {
    "openfang":
      {
        "emoji": "📐",
        "requires": { "bins": ["curl", "jq"], "env": ["LINEAR_API_KEY"] },
        "primaryEnv": "LINEAR_API_KEY",
      },
  }
---

# Linear

Manage issues, projects, and cycles via Linear's GraphQL API.

## Setup

1. Go to Settings → API → Personal API keys
2. Create a new key
3. Set environment variable:

```bash
export LINEAR_API_KEY="lin_api_..."  # pragma: allowlist secret
```

## Query Helper

All requests use this pattern:

```bash
curl -s https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "YOUR_QUERY"}' | jq
```

## List My Issues

```bash
curl -s https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ viewer { assignedIssues { nodes { identifier title state { name } priority } } } }"}' \
  | jq '.data.viewer.assignedIssues.nodes[] | {id: .identifier, title, state: .state.name, priority}'
```

## Search Issues

```bash
curl -s https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ issueSearch(query: \"bug\") { nodes { identifier title state { name } } } }"}' \
  | jq '.data.issueSearch.nodes[]'
```

## Get Issue Details

```bash
curl -s https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ issue(id: \"ISSUE_UUID\") { identifier title description state { name } assignee { name } comments { nodes { body user { name } } } } }"}' \
  | jq '.data.issue'
```

## Create Issue

```bash
curl -s https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation($input: IssueCreateInput!) { issueCreate(input: $input) { issue { identifier title url } } }",
    "variables": {
      "input": {
        "teamId": "TEAM_UUID",
        "title": "New issue title",
        "description": "Issue description here",
        "priority": 2
      }
    }
  }' | jq '.data.issueCreate.issue'
```

## Update Issue State

```bash
curl -s https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation($id: String!, $stateId: String!) { issueUpdate(id: $id, input: { stateId: $stateId }) { issue { identifier state { name } } } }",
    "variables": {
      "id": "ISSUE_UUID",
      "stateId": "STATE_UUID"
    }
  }' | jq
```

## Add Comment

```bash
curl -s https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation($input: CommentCreateInput!) { commentCreate(input: $input) { comment { body } } }",
    "variables": {
      "input": {
        "issueId": "ISSUE_UUID",
        "body": "Comment text here"
      }
    }
  }' | jq
```

## List Teams

```bash
curl -s https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ teams { nodes { id name key } } }"}' \
  | jq '.data.teams.nodes[]'
```

## List Workflow States

```bash
curl -s https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ workflowStates { nodes { id name type team { key } } } }"}' \
  | jq '.data.workflowStates.nodes[] | {id, name, type, team: .team.key}'
```

## List Projects

```bash
curl -s https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ projects { nodes { id name state } } }"}' \
  | jq '.data.projects.nodes[]'
```

## Current Cycle Issues

```bash
curl -s https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ cycles(filter: { isActive: { eq: true } }) { nodes { name issues { nodes { identifier title state { name } } } } } }"}' \
  | jq '.data.cycles.nodes[0].issues.nodes[]'
```

## Tips

- Issue IDs in URLs (e.g., `ENG-123`) are identifiers; API uses UUIDs internally
- Priority: 0 = No priority, 1 = Urgent, 2 = High, 3 = Medium, 4 = Low
- Use GraphQL introspection to explore schema: `{ __schema { types { name } } }`
