from __future__ import annotations

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from config.constants import SELECTORS, TIMEOUTS
from helpers.logger import get_logger
from helpers.screenshot import save_screenshot

logger = get_logger(__name__)


class PolicyService:
    def __init__(self, page: Page):
        self.page = page

    def click_policy(self) -> bool:
        """
        Clicks the first policy link on the customer detail page.
        Returns True if clicked, False if no policy link found.
        """
        logger.info("Looking for policy link")
        try:
            locator = self.page.locator(SELECTORS.POLICY_LINK).first

            if locator.count() == 0:
                logger.warning("No policy link found on page")
                return False

            locator.click(timeout=TIMEOUTS.DEFAULT)
            logger.info("Policy clicked — desktop window opening")
            return True
        except PlaywrightTimeoutError as e:
            save_screenshot(self.page, "policy_click_failed")
            logger.error(f"Policy click failed: {e}")
            raise
