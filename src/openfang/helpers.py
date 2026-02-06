"""Helper functions used across the openfang package."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import Page


def truncate_text(text: str, max_chars: int) -> tuple[str, str]:
    """Truncate text to max_chars, returning (truncated_text, suffix).

    Returns:
        Tuple of (text, suffix) where suffix is empty if no truncation,
        or a message like "... (truncated, 12345 chars total)" if truncated.
    """
    if len(text) <= max_chars:
        return text, ""
    return text[:max_chars], f"\n... (truncated, {len(text)} chars total)"


def format_page(page: Page, max_chars: int, include_url: bool = True) -> str:
    """Format a Page for tool output with truncation.

    Args:
        page: The Page to format.
        max_chars: Maximum characters for the text content.
        include_url: Whether to include the URL in output.
    """
    text, truncated = truncate_text(page.text, max_chars)
    if include_url:
        return f"Title: {page.title}\nURL: {page.url}\n\n{text}{truncated}"
    return f"Title: {page.title}\n\n{text}{truncated}"
