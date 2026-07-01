from __future__ import annotations

from pywinauto.base_wrapper import BaseWrapper

from desktop.policy_window.basic_info import BasicInfo
from desktop.policy_window.fee_handler import FeeHandler
from desktop.policy_window.reader import PolicyReader
from excel.models import FeeInfo, PolicyInfo
from helpers.logger import get_logger

logger = get_logger(__name__)


class PolicyWindowSession:
    """
    Single entry point for all operations inside the AMS360 Policy desktop window.
    Receives an already-attached window. Does not open or close it.
    """

    def __init__(self, window: BaseWrapper):
        self.window = window
        self._basic_info = BasicInfo(window)
        self._fee_handler = FeeHandler(window)
        self._reader = PolicyReader(window)

    def run(self, fee: FeeInfo) -> PolicyInfo:
        # 1 — Open Basic Policy Information and set Status based on policy period
        self._basic_info.open()
        period = self._reader.get_period()
        status = "Active" if period == "Annual" else "Non-renewed"
        logger.info(f"Policy period: {period} → Status: {status}")
        self._basic_info.set_status(status)

        # 2 — Add transaction fee
        self._fee_handler.add(charge_type=fee.charge_type, amount=fee.amount)

        # 3 — Read and return policy data
        policy_info = self._reader.read()
        return policy_info
