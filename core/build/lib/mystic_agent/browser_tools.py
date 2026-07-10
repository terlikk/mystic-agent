"""Browser skill — the agent drives a real headless browser so it can
research and *do* things on the web (bookings, forms, accounts).

By design it does the legwork and stops before the irreversible step:
payment / final confirmation stays a human decision (send a screenshot,
let the owner press the last button). Screenshots are pushed to the
owner so they can watch it work.

Optional dependency: pip install "mystic-agent[browser]" then
`python -m playwright install chromium`.
"""

import asyncio
from pathlib import Path
from typing import Any, Awaitable, Callable

from .tools import Tool

PhotoNotifier = Callable[[str, str], Awaitable[None]]  # (path, caption)


def browser_available() -> bool:
    try:
        import playwright.async_api  # noqa: F401

        return True
    except ImportError:
        return False


class BrowserSession:
    """A single persistent page the agent operates step by step."""

    def __init__(self, screenshots_dir: Path) -> None:
        self._dir = screenshots_dir
        self._dir.mkdir(parents=True, exist_ok=True)
        self._pw = None
        self._browser = None
        self._page = None
        self._lock = asyncio.Lock()
        self._shot = 0

    async def _ensure(self):
        if self._page is not None:
            return
        from playwright.async_api import async_playwright

        self._pw = await async_playwright().start()
        self._browser = await self._pw.chromium.launch(headless=True)
        self._page = await self._browser.new_page()

    async def open(self, url: str) -> str:
        async with self._lock:
            await self._ensure()
            await self._page.goto(url, wait_until="domcontentloaded", timeout=30000)
            return f"otwarto: {await self._page.title()} — {self._page.url}"

    async def read(self) -> str:
        async with self._lock:
            await self._ensure()
            text = await self._page.inner_text("body")
        return text[:4000].strip() or "(pusta strona)"

    async def click(self, target: str) -> str:
        async with self._lock:
            await self._ensure()
            page = self._page
            for locator in (
                page.get_by_role("button", name=target, exact=False),
                page.get_by_role("link", name=target, exact=False),
                page.get_by_text(target, exact=False),
            ):
                try:
                    await locator.first.click(timeout=4000)
                    await page.wait_for_load_state("domcontentloaded", timeout=8000)
                    return f"kliknięto: {target} → {page.url}"
                except Exception:
                    continue
            try:
                await page.click(target, timeout=4000)
                return f"kliknięto (selektor): {target}"
            except Exception:
                return f"nie znalazłem elementu: {target}"

    async def type(self, field: str, value: str, submit: bool = False) -> str:
        async with self._lock:
            await self._ensure()
            page = self._page
            for locator in (
                page.get_by_label(field),
                page.get_by_placeholder(field),
            ):
                try:
                    await locator.first.fill(value, timeout=4000)
                    if submit:
                        await locator.first.press("Enter")
                        await page.wait_for_load_state(
                            "domcontentloaded", timeout=8000
                        )
                    return f"wpisano „{value}” w: {field}"
                except Exception:
                    continue
            try:
                await page.fill(field, value, timeout=4000)
                return f"wpisano „{value}” w selektor: {field}"
            except Exception:
                return f"nie znalazłem pola: {field}"

    async def screenshot(self, caption: str, notify_photo: PhotoNotifier | None) -> str:
        async with self._lock:
            await self._ensure()
            self._shot += 1
            path = self._dir / f"shot-{self._shot}.png"
            await self._page.screenshot(path=str(path))
        if notify_photo is not None:
            await notify_photo(str(path), caption or "podgląd")
        return f"zrzut ekranu zapisany: {path}"

    async def close(self) -> None:
        if self._browser is not None:
            await self._browser.close()
        if self._pw is not None:
            await self._pw.stop()
        self._page = self._browser = self._pw = None


def browser_tools(
    session: BrowserSession, notify_photo: PhotoNotifier | None = None
) -> list[Tool]:
    async def browser_open(args: dict[str, Any]) -> str:
        return await session.open(str(args.get("url", "")))

    async def browser_read(_: dict[str, Any]) -> str:
        return await session.read()

    async def browser_click(args: dict[str, Any]) -> str:
        return await session.click(str(args.get("target", "")))

    async def browser_type(args: dict[str, Any]) -> str:
        return await session.type(
            str(args.get("field", "")),
            str(args.get("value", "")),
            bool(args.get("submit", False)),
        )

    async def browser_screenshot(args: dict[str, Any]) -> str:
        return await session.screenshot(
            str(args.get("caption", "")), notify_photo
        )

    cap = "browser"
    return [
        Tool(
            name="browser_open",
            capability=cap,
            description="Otwiera adres w przeglądarce agenta.",
            parameters={
                "type": "object",
                "properties": {"url": {"type": "string"}},
                "required": ["url"],
            },
            func=browser_open,
        ),
        Tool(
            name="browser_read",
            capability=cap,
            description="Zwraca widoczny tekst bieżącej strony.",
            parameters={"type": "object", "properties": {}},
            func=browser_read,
        ),
        Tool(
            name="browser_click",
            capability=cap,
            description="Klika przycisk/link po treści lub selektorze CSS.",
            parameters={
                "type": "object",
                "properties": {"target": {"type": "string"}},
                "required": ["target"],
            },
            func=browser_click,
        ),
        Tool(
            name="browser_type",
            capability=cap,
            description="Wpisuje tekst w pole (po etykiecie/placeholderze/selektorze);"
            " submit=true zatwierdza Enterem.",
            parameters={
                "type": "object",
                "properties": {
                    "field": {"type": "string"},
                    "value": {"type": "string"},
                    "submit": {"type": "boolean"},
                },
                "required": ["field", "value"],
            },
            func=browser_type,
        ),
        Tool(
            name="browser_screenshot",
            capability=cap,
            description="Robi zrzut ekranu strony i wysyła go użytkownikowi"
            " (pokaż postęp / poproś o ostatni klik).",
            parameters={
                "type": "object",
                "properties": {"caption": {"type": "string"}},
            },
            func=browser_screenshot,
        ),
    ]
