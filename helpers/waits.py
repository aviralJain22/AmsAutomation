from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Page


def wait_for_selector(page: "Page", selector: str, timeout: int = 30_000) -> None:
    page.wait_for_selector(selector, timeout=timeout)


def wait_for_url_contains(page: "Page", fragment: str, timeout: int = 60_000) -> None:
    page.wait_for_url(f"**{fragment}**", timeout=timeout)


def wait_for_navigation(page: "Page", timeout: int = 60_000) -> None:
    page.wait_for_load_state("networkidle", timeout=timeout)
