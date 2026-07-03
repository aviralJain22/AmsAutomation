from __future__ import annotations

from pywinauto.base_wrapper import BaseWrapper

from helpers.logger import get_logger

logger = get_logger(__name__)

DESCRIPTION_AUTO_ID = "txtEndorsement_Endorse_PolTDescription"
OK_BUTTON_AUTO_ID = "btnEndorsement_Endorse_EndorseOK"
CANCEL_BUTTON_AUTO_ID = "btnEndorsement_Endorse_EndorseCancel"


class EndorseWindowReader:
    def __init__(self, window: BaseWrapper):
        self.window = window

    def get_description(self) -> str:
        try:
            return self.window.child_window(
                auto_id=DESCRIPTION_AUTO_ID, control_type="Edit"
            ).get_value().strip()
        except Exception as e:
            logger.warning(f"Could not read Description: {e}")
            return ""

    def set_description(self, description: str) -> None:
        try:
            edit = self.window.child_window(auto_id=DESCRIPTION_AUTO_ID, control_type="Edit")
            edit.set_edit_text(description)
            logger.info(f"Description updated to '{description}'")
        except Exception as e:
            logger.warning(f"Could not set Description to '{description}': {e}")

    def click_ok(self) -> None:
        try:
            self.window.child_window(
                auto_id=OK_BUTTON_AUTO_ID, control_type="Button"
            ).click_input()
            logger.info("Clicked OK on Endorse window")
        except Exception as e:
            logger.warning(f"Could not click OK: {e}")

    def click_cancel(self) -> None:
        try:
            self.window.child_window(
                auto_id=CANCEL_BUTTON_AUTO_ID, control_type="Button"
            ).click_input()
            logger.info("Clicked Cancel on Endorse window")
        except Exception as e:
            logger.warning(f"Could not click Cancel: {e}")
