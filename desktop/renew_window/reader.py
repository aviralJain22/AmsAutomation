from __future__ import annotations

from pywinauto.base_wrapper import BaseWrapper
from pywinauto.controls.uiawrapper import UIAWrapper
from pywinauto.keyboard import send_keys
from pywinauto.uia_defines import IUIA
from pywinauto.uia_element_info import UIAElementInfo

from helpers.logger import get_logger

logger = get_logger(__name__)

POLICY_NO_AUTO_ID = "txtCopyPolicy_CopyPolCopyPol_BPolPolNo"
OK_BUTTON_AUTO_ID = "btnCopyPolicy_CopyPolCopyPol_CopyPolOK"
CANCEL_BUTTON_AUTO_ID = "btnCopyPolicy_CopyPolCopyPol_CopyPolCancel"


class RenewWindowReader:
    def __init__(self, window: BaseWrapper):
        self.window = window

    def get_policy_number(self) -> str:
        try:
            return self.window.child_window(
                auto_id=POLICY_NO_AUTO_ID, control_type="Edit"
            ).get_value().strip()
        except Exception as e:
            logger.warning(f"Could not read Policy #: {e}")
            return ""

    def set_policy_number(self, policy_number: str) -> None:
        try:
            edit = self.window.child_window(auto_id=POLICY_NO_AUTO_ID, control_type="Edit")
            edit.set_edit_text(policy_number)
            logger.info(f"Policy # updated to '{policy_number}'")
        except Exception as e:
            logger.warning(f"Could not set Policy # to '{policy_number}': {e}")

    def press_tab(self) -> None:
        send_keys("{TAB}")

    def get_focused_field_value(self) -> str:
        try:
            focused = UIAWrapper(UIAElementInfo(IUIA().get_focused_element()))
            return focused.get_value().strip()
        except Exception as e:
            logger.warning(f"Could not read focused field value: {e}")
            return ""

    def click_ok(self) -> None:
        try:
            self.window.child_window(
                auto_id=OK_BUTTON_AUTO_ID, control_type="Button"
            ).click_input()
            logger.info("Clicked OK on Renew window")
        except Exception as e:
            logger.warning(f"Could not click OK: {e}")

    def click_cancel(self) -> None:
        try:
            self.window.child_window(
                auto_id=CANCEL_BUTTON_AUTO_ID, control_type="Button"
            ).click_input()
            logger.info("Clicked Cancel on Renew window")
        except Exception as e:
            logger.warning(f"Could not click Cancel: {e}")
