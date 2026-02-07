"""File-based session storage using JSONL format."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic_ai.messages import ModelMessagesTypeAdapter

if TYPE_CHECKING:
    from pydantic_ai.messages import ModelMessage

logger = logging.getLogger(__name__)

# Version for future format migrations
TRANSCRIPT_VERSION = 1

# Type adapter for serializing/deserializing ModelMessage lists
_message_adapter = ModelMessagesTypeAdapter


class FileSessions:
    """File-based session storage using JSONL format.

    Each session is stored as a separate .jsonl file with:
    - Header line: {"type": "session", "version": 1, "id": "...", "timestamp": "..."}
    - Message lines: {"type": "message", "message": {...}}

    Similar to OpenClaw's transcript format.
    """

    def __init__(self, directory: str | Path) -> None:
        """Initialize file-based sessions.

        Args:
            directory: Directory to store session files (e.g. ~/.openfang/sessions)
        """
        self.directory = Path(directory).expanduser()
        self.directory.mkdir(parents=True, exist_ok=True)

    def _session_path(self, session_id: str) -> Path:
        """Get the file path for a session.

        Sanitizes the session_id to be filesystem-safe.
        """
        # Replace unsafe characters with underscores
        safe_id = session_id.replace("/", "_").replace("\\", "_").replace(":", "_")
        return self.directory / f"{safe_id}.jsonl"

    async def get(self, session_id: str) -> list[ModelMessage]:
        """Get all messages for a session."""
        path = self._session_path(session_id)
        if not path.exists():
            return []

        messages: list[ModelMessage] = []
        try:
            with path.open() as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    record = json.loads(line)
                    if record.get("type") == "message":
                        # Deserialize the message using pydantic-ai's adapter
                        msg_data = record.get("message")
                        if msg_data:
                            # Wrap in list for the type adapter, then extract
                            parsed = _message_adapter.validate_python([msg_data])
                            messages.extend(parsed)
        except Exception as e:
            logger.error(f"Error reading session {session_id}: {e}")
            return []

        return messages

    async def save(self, session_id: str, messages: list[ModelMessage]) -> None:
        """Save (replace) all messages for a session."""
        path = self._session_path(session_id)

        try:
            with path.open("w") as f:
                # Write header
                header = {
                    "type": "session",
                    "version": TRANSCRIPT_VERSION,
                    "id": session_id,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
                f.write(json.dumps(header) + "\n")

                # Write messages - use dump_json for proper datetime handling
                for msg in messages:
                    # Serialize single message by wrapping in list
                    msg_json = _message_adapter.dump_json([msg])
                    # Parse back to get the dict, then extract first item
                    msg_data = json.loads(msg_json)[0]
                    record = {"type": "message", "message": msg_data}
                    f.write(json.dumps(record) + "\n")
        except Exception as e:
            logger.error(f"Error saving session {session_id}: {e}")
            raise

    async def append(self, session_id: str, messages: list[ModelMessage]) -> None:
        """Append messages to a session."""
        path = self._session_path(session_id)

        try:
            # If file doesn't exist, write header first
            if not path.exists():
                with path.open("w") as f:
                    header = {
                        "type": "session",
                        "version": TRANSCRIPT_VERSION,
                        "id": session_id,
                        "timestamp": datetime.now(UTC).isoformat(),
                    }
                    f.write(json.dumps(header) + "\n")

            # Append messages
            with path.open("a") as f:
                for msg in messages:
                    msg_json = _message_adapter.dump_json([msg])
                    msg_data = json.loads(msg_json)[0]
                    record = {"type": "message", "message": msg_data}
                    f.write(json.dumps(record) + "\n")
        except Exception as e:
            logger.error(f"Error appending to session {session_id}: {e}")
            raise

    async def delete(self, session_id: str) -> None:
        """Delete a session and its file."""
        path = self._session_path(session_id)
        if path.exists():
            path.unlink()

    async def list(self, user_id: int | None = None) -> list[str]:
        """List all session IDs.

        Note: user_id filtering is not supported for file-based storage.
        All sessions are returned.
        """
        sessions = []
        for path in self.directory.glob("*.jsonl"):
            # Read the header to get the actual session ID
            try:
                with path.open() as f:
                    first_line = f.readline().strip()
                    if first_line:
                        header = json.loads(first_line)
                        if header.get("type") == "session":
                            sessions.append(header.get("id", path.stem))
                        else:
                            # Old format or no header, use filename
                            sessions.append(path.stem)
            except Exception:
                # Fallback to filename
                sessions.append(path.stem)

        return sessions
