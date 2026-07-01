from __future__ import annotations

from browser.browser_manager import BrowserManager
from browser.customer_service import CustomerService
from browser.login_service import LoginService
from browser.policy_service import PolicyService
from desktop.orchestrator import DesktopOrchestrator
from excel.excel_service import ExcelService
from helpers.logger import get_logger

logger = get_logger(__name__)


class AMS360Workflow:
    def __init__(self, headless: bool = False):
        self.browser_manager = BrowserManager(headless=headless)
        self.desktop = DesktopOrchestrator()
        self.excel_service = ExcelService()

    def run(self) -> None:
        customer = self.excel_service.get_customer()
        fee = self.excel_service.get_fee_info()
        logger.info(f"Starting workflow for customer: {customer.name}")

        page = self.browser_manager.start()
        try:
            LoginService(page).login()
            CustomerService(page).search(customer.name)

            policy_found = PolicyService(page).click_policy()
            if not policy_found:
                logger.warning(f"No policy found for '{customer.name}' — stopping")
                return

            policy_info = self.desktop.run_policy_flow(customer=customer, fee=fee)
            
            self.excel_service.write_policy(policy_info)

            logger.info("Workflow completed successfully")

        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            raise

        finally:
            self.browser_manager.stop()
