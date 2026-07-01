from __future__ import annotations

import time

from pywinauto.base_wrapper import BaseWrapper

from helpers.logger import get_logger

logger = get_logger(__name__)

BASIC_INFO_PANE_AUTO_ID = "sctPolicy_PolBPolInfo"
# TODO: run tools/inspect_window.py on expanded Basic Policy Info section to confirm this auto_id
STATUS_AUTO_ID = "TODO_STATUS_AUTO_ID"


class BasicInfo:
    def __init__(self, window: BaseWrapper):
        self.window = window

    def open(self) -> None:
        """Expand the Basic Policy Information section."""
        logger.info("Opening Basic Policy Information section")
        try:
            pane = self.window.child_window(auto_id=BASIC_INFO_PANE_AUTO_ID, control_type="Pane")
            pane.click_input()
            time.sleep(1)
            logger.info("Basic Policy Information section opened")
        except Exception as e:
            logger.warning(f"Could not open Basic Policy Information: {e}")

    def set_status(self, status: str) -> None:
        """Set the Status dropdown. status should be 'Active' or 'Non-renewed'."""
        logger.info(f"Setting Status: '{status}'")
        try:
            combo = self.window.child_window(auto_id=STATUS_AUTO_ID, control_type="ComboBox")
            combo.select(status)
            logger.info(f"Status set: '{status}'")
        except Exception as e:
            logger.warning(f"Could not set Status '{status}': {e}")
