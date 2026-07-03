from __future__ import annotations

import time

from pywinauto.base_wrapper import BaseWrapper

from config.constants import TIMEOUTS
from desktop.renew_window.reader import RenewWindowReader
from helpers.logger import get_logger

logger = get_logger(__name__)


class RenewWindowSession:
    """
    Single entry point for operations inside the AMS360 Create Renewal/Rewrite
    Policy desktop window. Receives an already-attached window.
    """

    def __init__(self, window: BaseWrapper):
        self.window = window
        self._reader = RenewWindowReader(window)

    def run(self, excel_policy_number: str) -> Boolean:
        current_policy_number = self._reader.get_policy_number()
        logger.info(f"Renew window Policy #: '{current_policy_number}'")
        time.sleep(TIMEOUTS.RENEW_STEP_WAIT)

        self._reader.press_tab()
        effective_date = self._reader.get_focused_field_value()
        logger.info(f"Renew window Effective Date: '{effective_date}'")
        time.sleep(TIMEOUTS.RENEW_STEP_WAIT)

        self._reader.press_tab()
        expiration_date = self._reader.get_focused_field_value()
        logger.info(f"Renew window Expiration Date: '{expiration_date}'")
        time.sleep(TIMEOUTS.RENEW_STEP_WAIT)

        self._reader.set_policy_number(excel_policy_number)
        time.sleep(TIMEOUTS.RENEW_STEP_WAIT)

        # Clicking OK (not Cancel) submits the renewal — AMS360 then closes
        # this window and opens the new Policy window automatically.
        self._reader.click_ok()

        self._reader.click_cancel()