from __future__ import annotations

from config.constants import WINDOW_TITLES
from desktop.desktop_manager import DesktopManager
from desktop.policy_window import PolicyWindowSession
from excel.models import CustomerInfo, FeeInfo, PolicyInfo
from helpers.logger import get_logger

logger = get_logger(__name__)


class DesktopOrchestrator:
    """
    Coordinates multi-window desktop flows.
    The workflow calls one method here — this class decides which windows
    open, in what order, and what to do in each.
    """

    def __init__(self):
        self._manager = DesktopManager()

    def run_policy_flow(self, customer: CustomerInfo, fee: FeeInfo) -> PolicyInfo:
        """
        Full policy desktop flow:
          1. Attach and maximize the Policy window
          2. Run PolicyWindowSession (basic info → fee → read)
          3. Close the Policy window
          4. Return PolicyInfo
        """
        logger.info("Desktop orchestrator: starting policy flow")

        self._manager.wait_window(WINDOW_TITLES.POLICY_WINDOW)
        window = self._manager.attach(WINDOW_TITLES.POLICY_WINDOW)
        self._manager.maximize(window)

        try:
            policy_info = PolicyWindowSession(window).run(fee=fee)
            policy_info.customer_name = customer.name
            policy_info.customer_address = customer.address
        finally:
            self._manager.close(window)

        logger.info("Desktop orchestrator: policy flow complete")
        return policy_info
