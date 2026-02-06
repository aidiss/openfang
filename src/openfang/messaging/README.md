# Messaging

Message routing from channels to agent and back.

Flow: `Channel → InboundMessage → Dispatcher → Agent → Response → Channel`

Key files:
- `resolver.py` - Creates session keys: `{channel}:{account}:{peer_kind}:{peer_id}`
- `dispatcher.py` - Routes messages to agent, sends responses back
