from dataclasses import dataclass


@dataclass(frozen=True)
class _Timeouts:
    DEFAULT: int = 30_000       # ms — Playwright default
    LOGIN: int = 60_000
    DASHBOARD: int = 30_000
    SEARCH_RESULTS: int = 30_000
    POLICY_WINDOW: int = 30     # seconds — pywinauto
    RENEW_WINDOW: int = 30      # seconds — pywinauto
    ENDORSE_WINDOW: int = 30    # seconds — pywinauto
    WINDOW_CLOSE_WAIT: int = 30  # seconds — wait before closing desktop window
    RENEW_STEP_WAIT: float = 1  # seconds — pause between steps in the Renew window


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

    # Policy grid (ExtJS) — scoped to the grid whose header has a "Policy" column,
    # since the page can contain more than one x-grid3 widget.
    POLICY_GRID_VIEWPORT: str = "div.x-grid3-viewport:has(.x-grid3-hd-Policy)"
    POLICY_GRID_ROW: str = "div.x-grid3-viewport:has(.x-grid3-hd-Policy) div.x-grid3-row"
    POLICY_GRID_POLICY_NUMBER: str = "td.x-grid3-td-Policy a"
    POLICY_GRID_TERM_CELL: str = "td.x-grid3-td-Term"

    # Action buttons — AMS360 toolbar
    RENEW_BUTTON: str = "//button[normalize-space()='Renew']"
    ENDORSE_BUTTON: str = "//button[normalize-space()='Endorse']"

    # Policy (legacy single-link click)
    POLICY_LINK: str = "a.policy.launchPolicy.link"


@dataclass(frozen=True)
class _WindowTitles:
    POLICY_WINDOW: str = "Policy"     # partial match — adjust to actual AMS360 window title
    RENEW_WINDOW: str = "Create Renewal/Rewrite Policy*"  # partial match — title ends with the actual policy number
    ENDORSE_WINDOW: str = "Endorsement"  # partial match
    RECEIPT_WINDOW: str = "Receipt"  # partial match — adjust once the real window is inspected

TIMEOUTS = _Timeouts()
SELECTORS = _Selectors()
WINDOW_TITLES = _WindowTitles()

EXCEL_HEADERS = ["Policy Number", "Effective Date", "Expiration Date", "Premium", "Status", "Fees", "Annualized Premium", "Bill Method", "Customer Name", "Customer Address"]
SCREENSHOTS_DIR = "screenshots"
LOGS_DIR = "logs"
LOG_FILE = "logs/ams360.log"
