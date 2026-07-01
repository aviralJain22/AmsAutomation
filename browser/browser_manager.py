from __future__ import annotations

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, Playwright

from helpers.logger import get_logger

logger = get_logger(__name__)


class BrowserManager:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    def start(self) -> Page:
        logger.info("Starting browser")
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=self.headless)
        self._context = self._browser.new_context()
        self._page = self._context.new_page()
        logger.info("Browser started")
        return self._page

    def stop(self) -> None:
        logger.info("Stopping browser")
        try:
            if self._context:
                self._context.close()
            if self._browser:
                self._browser.close()
            if self._playwright:
                self._playwright.stop()
        except Exception as e:
            logger.warning(f"Error during browser teardown: {e}")
        finally:
            self._page = self._context = self._browser = self._playwright = None
        logger.info("Browser stopped")
