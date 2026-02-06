"""Web access using Playwright."""

from __future__ import annotations

import httpx
from playwright.async_api import async_playwright

from openfang.types import Page


class PlaywrightSession:
    """Stateful browser session using Playwright."""

    def __init__(self, playwright, browser, page):
        self._pw = playwright
        self._browser = browser
        self._page = page

    async def goto(self, url: str) -> Page:
        await self._page.goto(url, wait_until="domcontentloaded")
        return Page(
            url=self._page.url,
            title=await self._page.title(),
            text=await self._page.inner_text("body"),
            html=await self._page.content(),
        )

    async def click(self, selector: str) -> Page:
        await self._page.click(selector)
        await self._page.wait_for_load_state("domcontentloaded")
        return Page(
            url=self._page.url,
            title=await self._page.title(),
            text=await self._page.inner_text("body"),
            html=await self._page.content(),
        )

    async def type(self, selector: str, text: str) -> None:
        await self._page.fill(selector, text)

    async def screenshot(self) -> bytes:
        return await self._page.screenshot()

    async def close(self) -> None:
        await self._browser.close()
        await self._pw.stop()


class PlaywrightWeb:
    """Web access using Playwright."""

    async def fetch(self, url: str) -> str:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get(url)
            return resp.text

    async def browse(self, url: str) -> Page:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded")
            result = Page(
                url=page.url,
                title=await page.title(),
                text=await page.inner_text("body"),
                html=await page.content(),
            )
            await browser.close()
            return result

    async def screenshot(self, url: str) -> bytes:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded")
            data = await page.screenshot()
            await browser.close()
            return data

    async def session(self) -> PlaywrightSession:
        pw = await async_playwright().start()
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        return PlaywrightSession(pw, browser, page)
