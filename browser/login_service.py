from __future__ import annotations

import time

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from config.constants import SELECTORS, TIMEOUTS
from config.settings import settings
from helpers.logger import get_logger
from helpers.screenshot import save_screenshot
from helpers.waits import wait_for_selector

logger = get_logger(__name__)


class LoginService:
    def __init__(self, page: Page):
        self.page = page

    def _is_already_logged_in(self) -> bool:
        try:
            self.page.wait_for_load_state("networkidle", timeout=5_000)
            return SELECTORS.EMAIL_INPUT not in (self.page.content() or "")
        except PlaywrightTimeoutError:
            return False

    def login(self) -> None:
        logger.info(f"Navigating to {settings.ams360_url}")
        try:
            self.page.goto(settings.ams360_url, timeout=TIMEOUTS.LOGIN)

            # if self._is_already_logged_in():
            #     logger.info("Already logged in — navigating to post-login URL")
            #     self.page.goto(settings.ams360_url_if_login, timeout=TIMEOUTS.LOGIN)
            #     self.page.wait_for_load_state("networkidle", timeout=TIMEOUTS.DASHBOARD)
            #     return

            # Step 1 — email
            wait_for_selector(self.page, SELECTORS.EMAIL_INPUT, timeout=TIMEOUTS.LOGIN)
            self.page.fill(SELECTORS.EMAIL_INPUT, settings.username)
            self.page.click(SELECTORS.EMAIL_NEXT_BUTTON)
            logger.info("Step 1 complete — email submitted")

            # Step 2 — password
            wait_for_selector(self.page, SELECTORS.PASSWORD_INPUT, timeout=TIMEOUTS.LOGIN)
            self.page.fill(SELECTORS.PASSWORD_INPUT, settings.password)
            self.page.click(SELECTORS.LOGIN_BUTTON)

            self.page.wait_for_load_state("networkidle", timeout=TIMEOUTS.DASHBOARD)
            time.sleep(TIMEOUTS.DEFAULT / 1000)
            logger.info("Login successful — dashboard loaded")
        except PlaywrightTimeoutError as e:
            save_screenshot(self.page, "login_failed")
            logger.error(f"Login failed: {e}")
            raise
