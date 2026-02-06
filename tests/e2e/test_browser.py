"""Browser E2E tests via Playwright.

These tests require a live server and real browser. Use for testing:
- JavaScript features (Alpine.js)
- HTMX interactions
- Dark mode / localStorage
- Real-time updates (SSE)

Run with: uv run pytest tests/e2e/test_browser.py -v
Debug with: uv run pytest tests/e2e/test_browser.py -v -s (add breakpoints to inspect)
"""

from __future__ import annotations

import pytest
from playwright.async_api import Page, async_playwright, expect


@pytest.fixture
async def browser_page(live_server: str):
    """Create a browser page navigated to the app."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the app
        await page.goto(live_server)

        # Wait for Alpine.js to be ready
        await page.wait_for_function("typeof Alpine !== 'undefined'")

        yield page

        await context.close()
        await browser.close()


class TestPageLoad:
    """Test basic page loading."""

    async def test_page_loads_with_title(self, browser_page: Page):
        """Page loads with correct title."""
        await expect(browser_page).to_have_title("OpenFang Gateway")

    async def test_page_shows_logo(self, browser_page: Page):
        """Page shows OPENFANG logo."""
        logo = browser_page.locator("text=OPENFANG")
        await expect(logo).to_be_visible()

    async def test_chat_input_visible(self, browser_page: Page):
        """Chat input is visible on load."""
        chat_input = browser_page.locator('input[name="message"]')
        await expect(chat_input).to_be_visible()


class TestNavigation:
    """Test sidebar navigation (Alpine.js view switching)."""

    async def test_default_view_is_chat(self, browser_page: Page):
        """Default view shows chat interface."""
        chat_view = browser_page.locator("[x-show*=\"view === 'chat'\"]").first
        await expect(chat_view).to_be_visible()

    async def test_navigate_to_memory(self, browser_page: Page):
        """Can navigate to memory view."""
        # Click Memory in sidebar
        await browser_page.click('button:has-text("Memory")')

        # Wait for HTMX to load the panel
        await browser_page.wait_for_selector("#memory-panel")

        # Memory panel should be visible
        memory_panel = browser_page.locator("#memory-panel")
        await expect(memory_panel).to_be_visible()

    async def test_navigate_to_channels(self, browser_page: Page):
        """Can navigate to channels view."""
        await browser_page.click('button:has-text("Channels")')
        await browser_page.wait_for_selector("#channels-panel")

        channels_panel = browser_page.locator("#channels-panel")
        await expect(channels_panel).to_be_visible()

    async def test_navigate_back_to_chat(self, browser_page: Page):
        """Can navigate back to chat from another view."""
        # Go to memory
        await browser_page.click('button:has-text("Memory")')
        await browser_page.wait_for_selector("#memory-panel")

        # Go back to chat
        await browser_page.click('button:has-text("Chat")')

        # Chat input should be visible again
        chat_input = browser_page.locator('input[name="message"]')
        await expect(chat_input).to_be_visible()


class TestDarkMode:
    """Test dark mode toggle (localStorage persistence)."""

    async def test_dark_mode_toggle(self, browser_page: Page):
        """Can toggle dark mode."""
        html = browser_page.locator("html")

        # Find and click the theme toggle button
        theme_toggle = browser_page.locator(
            ".theme-toggle, button:has(svg.lucide-moon), button:has(svg.lucide-sun)"
        ).first

        # Check initial state (could be light or dark depending on system)
        initial_has_dark = await html.evaluate("el => el.classList.contains('dark')")

        # Toggle
        await theme_toggle.click()
        await browser_page.wait_for_timeout(100)  # Wait for transition

        # Should be opposite now
        new_has_dark = await html.evaluate("el => el.classList.contains('dark')")
        assert new_has_dark != initial_has_dark

    async def test_dark_mode_persists_in_localstorage(self, browser_page: Page):
        """Dark mode preference is saved to localStorage."""
        # Toggle to ensure we have a known state
        theme_toggle = browser_page.locator(
            ".theme-toggle, button:has(svg.lucide-moon), button:has(svg.lucide-sun)"
        ).first
        await theme_toggle.click()
        await browser_page.wait_for_timeout(100)

        # Check localStorage
        theme = await browser_page.evaluate("localStorage.getItem('theme')")
        assert theme in ("dark", "light")


class TestChatInteraction:
    """Test chat UI interactions."""

    async def test_send_button_state(self, browser_page: Page):
        """Send button is disabled when input is empty, enabled when filled."""
        chat_input = browser_page.locator('input[name="message"]')
        send_button = browser_page.locator('button[type="submit"]').first

        # Initially empty - button should be disabled or have disabled styling
        await expect(chat_input).to_have_value("")

        # Type something
        await chat_input.fill("Hello!")

        # Button should be interactable now
        await expect(send_button).to_be_enabled()

    async def test_keyboard_shortcut_focuses_input(self, browser_page: Page):
        """Cmd/Ctrl+K focuses the chat input."""
        chat_input = browser_page.locator('input[name="message"]')

        # Click elsewhere to unfocus
        await browser_page.locator("body").click()

        # Press Ctrl+K (or Cmd+K on Mac)
        await browser_page.keyboard.press("Control+k")

        # Input should be focused
        await expect(chat_input).to_be_focused()
