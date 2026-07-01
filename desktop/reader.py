from __future__ import annotations

import re

from pywinauto.base_wrapper import BaseWrapper

from excel.models import PolicyInfo
from helpers.logger import get_logger

logger = get_logger(__name__)

# Window title pattern: "Policy - James M Seymour - ACI04B11019405 - (7/20/2026 - 7/20/2027) - [Policy Information]"
_TITLE_RE = re.compile(
    r"Policy\s+-\s+.+?\s+-\s+(?P<policy_no>\S+)\s+-\s+\((?P<eff>[^-]+?)\s+-\s+(?P<exp>[^)]+?)\)"
)


class PolicyReader:
    def __init__(self, window: BaseWrapper):
        self.window = window

    def _get_edit_value(self, auto_id: str) -> str:
        try:
            return self.window.child_window(auto_id=auto_id, control_type="Edit").get_value().strip()
        except Exception as e:
            logger.warning(f"Could not read '{auto_id}': {e}")
            return ""

    def _parse_title(self) -> dict:
        try:
            title = self.window.window_text()
            m = _TITLE_RE.search(title)
            if m:
                return {
                    "policy_number": m.group("policy_no").strip(),
                    "effective_date": m.group("eff").strip(),
                    "expiration_date": m.group("exp").strip(),
                }
        except Exception as e:
            logger.warning(f"Could not parse window title: {e}")
        return {"policy_number": "", "effective_date": "", "expiration_date": ""}

    def get_premium(self) -> str:
        return self._get_edit_value("txtPolicy_PolPremNonPrem_PolTPPolPremium")

    def get_fees_and_taxes(self) -> str:
        return self._get_edit_value("txtPolicy_PolPremNonPrem_PolTPPolFeesTaxes")

    def get_annualized_premium(self) -> str:
        return self._get_edit_value("txtPolicy_PolPremNonPrem_PolTPPolAnnualizedPremium")

    def get_bill_method(self) -> str:
        try:
            combo = self.window.child_window(
                auto_id="cmbPolicy_PolPremNonPrem_PolInvoicing_PolCmbInvoicingBillmethod",
                control_type="ComboBox",
            )
            return combo.selected_text().strip()
        except Exception as e:
            logger.warning(f"Could not read Bill Method: {e}")
            return ""

    def read(self) -> PolicyInfo:
        logger.info("Reading policy data from desktop window")
        title_data = self._parse_title()
        info = PolicyInfo(
            policy_number=title_data["policy_number"],
            effective_date=title_data["effective_date"],
            expiration_date=title_data["expiration_date"],
            premium=self.get_premium(),
            fees=self.get_fees_and_taxes(),
            annualized_premium=self.get_annualized_premium(),
            bill_method=self.get_bill_method(),
            status="Active",
        )
        logger.info(f"Policy read: {info}")
        return info
