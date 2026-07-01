from __future__ import annotations

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from config.constants import SELECTORS, TIMEOUTS
from helpers.logger import get_logger
from helpers.screenshot import save_screenshot
from helpers.waits import wait_for_selector
from config.settings import settings 

logger = get_logger(__name__)


class CustomerService:
    def __init__(self, page: Page):
        self.page = page

    def search(self, customer_name: str) -> None:
        logger.info(f"Searching for customer: {customer_name}")
        try:
            
            # Wait for AMS360's post-login redirect to /Home to fully settle
            self.page.wait_for_url("**/Home**", timeout=TIMEOUTS.DASHBOARD)
            self.page.wait_for_load_state("networkidle", timeout=TIMEOUTS.DEFAULT)
            self.page.goto(settings.customer_url, timeout=TIMEOUTS.LOGIN, wait_until="networkidle")
            wait_for_selector(self.page, SELECTORS.CUSTOMER_SEARCH_INPUT, timeout=TIMEOUTS.DEFAULT)

            self.page.fill(SELECTORS.CUSTOMER_SEARCH_INPUT, customer_name)
            self.page.keyboard.press("Enter")

            # Wait for AMS360 to navigate to the customer detail page
            self.page.wait_for_load_state("networkidle", timeout=TIMEOUTS.SEARCH_RESULTS)
            wait_for_selector(self.page, SELECTORS.POLICY_LINK, timeout=TIMEOUTS.SEARCH_RESULTS)
            logger.info(f"Customer detail page loaded for: {customer_name}")
        except PlaywrightTimeoutError as e:
            save_screenshot(self.page, "customer_search_failed")
            logger.error(f"Customer search failed: {e}")
            raise
