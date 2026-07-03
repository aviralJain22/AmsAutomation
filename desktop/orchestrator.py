from __future__ import annotations

from config.constants import TIMEOUTS, WINDOW_TITLES
from desktop.desktop_manager import DesktopManager
from desktop.endorse_window import EndorseWindowSession
from desktop.policy_window import PolicyWindowSession
from desktop.receipt_window import ReceiptWindowSession
from desktop.renew_window import RenewWindowSession
from excel.models import CustomerInfo, FeeInfo, PolicyInfo, PolicyInstruction
from helpers.logger import get_logger

logger = get_logger(__name__)


class DesktopOrchestrator:
    """
    Coordinates multi-window desktop flows.
    The workflow calls one method here — this class decides which windows
    open, in what order, and what to do in each, based on the action
    performed on the browser side (Renew / Endorse / Policy / Receipt).
    """

    def __init__(self):
        self._manager = DesktopManager()

    def run_flow(
        self, action: str, customer: CustomerInfo, fee: FeeInfo, instruction: PolicyInstruction
    ) -> PolicyInfo | None:
        logger.info(f"Desktop orchestrator: starting '{action}' flow")

        if action == "Renew":
            self._run_renew_flow(instruction)
        elif action == "Endorse":
            self._run_endorse_flow(instruction)
        elif action == "Receipt":
            self._run_receipt_flow()
        else:
            return self.run_policy_flow(customer=customer, fee=fee)

        logger.info(f"Desktop orchestrator: '{action}' flow complete")
        return None

    def run_policy_flow(self, customer: CustomerInfo, fee: FeeInfo) -> PolicyInfo:
        """
        Full policy desktop flow:
          1. Attach and maximize the Policy window
          2. Run PolicyWindowSession (basic info → fee → read)
          3. Close the Policy window
          4. Return PolicyInfo
        """
        window = self._attach(WINDOW_TITLES.POLICY_WINDOW)
        try:
            policy_info = PolicyWindowSession(window).run(fee=fee)
            policy_info.customer_name = customer.name
            policy_info.customer_address = customer.address
        finally:
            self._manager.close(window)

        return policy_info

    def _run_renew_flow(self, instruction: PolicyInstruction) -> None:
        window = self._attach(WINDOW_TITLES.RENEW_WINDOW, timeout=TIMEOUTS.RENEW_WINDOW)
        try:
            RenewWindowSession(window).run(instruction.policy_number)
        finally:
            self._manager.close(window)

    def _run_endorse_flow(self, instruction: PolicyInstruction) -> None:
        window = self._attach(WINDOW_TITLES.ENDORSE_WINDOW, timeout=TIMEOUTS.ENDORSE_WINDOW)
        try:
            EndorseWindowSession(window).run(instruction.endorsement_description)
        finally:
            self._manager.close(window)

    def _run_receipt_flow(self) -> None:
        window = self._attach(WINDOW_TITLES.RECEIPT_WINDOW)
        try:
            ReceiptWindowSession(window).run()
        finally:
            self._manager.close(window)

    def _attach(self, title: str, timeout: int = TIMEOUTS.POLICY_WINDOW):
        self._manager.wait_window(title, timeout=timeout)
        window = self._manager.attach(title)
        self._manager.maximize(window)
        return window
