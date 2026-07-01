from __future__ import annotations

import time

from pywinauto.base_wrapper import BaseWrapper
from pywinauto.keyboard import send_keys

from helpers.logger import get_logger

logger = get_logger(__name__)

FEES_PANE_AUTO_ID   = "sctPolicy_PolPremNonPrem_PolFeesTax"
FORM_PANE_AUTO_ID   = "Dialog"
CHARGE_TYPE_AUTO_ID = "cmbPolicy_PolPremNonPrem_PolFeesTax_PolCmbFeesTaxChargeType"
AMOUNT_AUTO_ID      = "txtPolicy_PolPremNonPrem_PolFeesTax_PolTPPremium"
ADD_FIRST_INST_AUTO_ID = "chkPolicy_PolPremNonPrem_PolFeesTax_PolTPNonPrinstTreatPolTP"
DONT_INCLUDE_AUTO_ID   = "radPolicy_PolPremNonPrem_PolFeesTaxPolGrpPremOptionDontInclude_PolTPIncludePremium"


class FeeHandler:
    def __init__(self, window: BaseWrapper):
        self.window = window

    def _fees_pane(self) -> BaseWrapper:
        return self.window.child_window(auto_id=FEES_PANE_AUTO_ID, control_type="Pane")

    def _click_hyperlink(self, pane: BaseWrapper, title: str) -> None:
        btn = pane.child_window(title=title, control_type="Hyperlink")
        try:
            btn.invoke()
        except Exception:
            btn.click_input()

    def add(self, charge_type: str, amount: str) -> None:
        """
        Click New → Set Charge Type → Set Amount →
        Check 'Add full amount to first installment' →
        Select 'Don't Include in Premium Totals' →
        Wait 10s → Click Cancel
        """
        fees_pane = self._fees_pane()

        logger.info("Clicking 'New' in Transaction Fees section")
        self._click_hyperlink(fees_pane, "New")

        logger.info("Waiting 10s for edit form to load...")
        time.sleep(10)

        form_pane = fees_pane.child_window(auto_id=FORM_PANE_AUTO_ID, control_type="Pane")

        # Set Charge Type
        logger.info(f"Setting Charge Type: '{charge_type}'")
        try:
            form_pane.child_window(auto_id=CHARGE_TYPE_AUTO_ID, control_type="ComboBox").select(charge_type)
        except Exception as e:
            logger.warning(f"ComboBox select failed, typing: {e}")
            form_pane.child_window(auto_id=CHARGE_TYPE_AUTO_ID, control_type="ComboBox").set_focus()
            send_keys(charge_type + "{ENTER}")

        # Set Amount
        logger.info(f"Setting Amount: '{amount}'")
        try:
            form_pane.child_window(auto_id=AMOUNT_AUTO_ID, control_type="Edit").set_text(amount)
        except Exception as e:
            logger.warning(f"Could not set Amount: {e}")

        # Check 'Add full amount to first installment'
        logger.info("Checking 'Add full amount to first installment'")
        try:
            form_pane.child_window(auto_id=ADD_FIRST_INST_AUTO_ID, control_type="CheckBox").check()
        except Exception as e:
            logger.warning(f"Could not check 'Add full amount to first installment': {e}")

        # Select 'Don't Include in Premium Totals'
        logger.info("Selecting 'Don't Include in Premium Totals'")
        try:
            form_pane.child_window(auto_id=DONT_INCLUDE_AUTO_ID, control_type="RadioButton").select()
        except Exception as e:
            logger.warning(f"Could not select 'Don't Include in Premium Totals': {e}")

        logger.info("Waiting 10s...")
        time.sleep(10)

        logger.info("Clicking Cancel")
        self._click_hyperlink(fees_pane, "Cancel")
        logger.info("Fee entry cancelled")
