from dataclasses import dataclass


@dataclass(frozen=True)
class _Timeouts:
    DEFAULT: int = 30_000       # ms — Playwright default
    LOGIN: int = 60_000
    DASHBOARD: int = 60_000
    SEARCH_RESULTS: int = 30_000
    POLICY_WINDOW: int = 30     # seconds — pywinauto
    WINDOW_CLOSE_WAIT: int = 30  # seconds — wait before closing desktop window


@dataclass(frozen=True)
class _Selectors:
    # Login — step 1 (email)
    EMAIL_INPUT: str = "#identifierInput"
    EMAIL_NEXT_BUTTON: str = "#postButton"

    # Login — step 2 (password)
    PASSWORD_INPUT: str = "#password"
    LOGIN_BUTTON: str = "[title='Log In']"

    DASHBOARD_INDICATOR: str = "#dashboard"

    # Customers
    CUSTOMERS_NAV: str = "text=Customers"
    CUSTOMER_SEARCH_INPUT: str = "#search-text"
    CUSTOMER_SUMMARY_BODY: str = ".summary-body"

    # Policy
    POLICY_LINK: str = "a.policy.launchPolicy.link"


@dataclass(frozen=True)
class _WindowTitles:
    POLICY_WINDOW: str = "Policy"     # partial match — adjust to actual AMS360 window title


TIMEOUTS = _Timeouts()
SELECTORS = _Selectors()
WINDOW_TITLES = _WindowTitles()

EXCEL_HEADERS = ["Policy Number", "Effective Date", "Expiration Date", "Premium", "Status", "Fees", "Annualized Premium", "Bill Method", "Customer Name", "Customer Address"]
SCREENSHOTS_DIR = "screenshots"
LOGS_DIR = "logs"
LOG_FILE = "logs/ams360.log"
