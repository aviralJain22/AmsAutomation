from __future__ import annotations

from typing import Literal

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from browser.policy_grid import PolicyGrid
from config.constants import SELECTORS, TIMEOUTS
from helpers.logger import get_logger
from helpers.screenshot import save_screenshot

logger = get_logger(__name__)


class PolicyService:
    def __init__(self, page: Page):
        self.page = page
        self.grid = PolicyGrid(page)

    # def click_policy(self) -> bool:
    #     """Legacy: clicks the first policy link without row matching."""
    #     logger.info("Looking for policy link")
    #     try:
    #         locator = self.page.locator(SELECTORS.POLICY_LINK).first
    #         if locator.count() == 0:
    #             logger.warning("No policy link found on page")
    #             return False
    #         locator.click(timeout=TIMEOUTS.DEFAULT)
    #         logger.info("Policy clicked — desktop window opening")
    #         return True
    #     except PlaywrightTimeoutError as e:
    #         save_screenshot(self.page, "policy_click_failed")
    #         logger.error(f"Policy click failed: {e}")
    #         raise

    def perform_grid_action(
        self,
        policy_number: str,
        effective_date: str,
        expiration_date: str,
        action: Literal["Renew", "Endorse"],
    ) -> bool:
        """
        Finds the matching row in the policy grid, selects it, then clicks
        the Renew or Endorse toolbar button.
        Returns True on success, False if no matching row was found.
        """
        return self.grid.perform_action(
            policy_number=policy_number,
            effective_date=effective_date,
            expiration_date=expiration_date,
            action=action,
        )
