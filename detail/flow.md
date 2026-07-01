# AMS360 Automation — Complete Flow

## Overview

This document describes the full automation flow from script start to Excel output.
Each step lists the file responsible, the action taken, and what happens next.

---

## Step 1 — Start Browser

**File:** `browser/browser_manager.py` → `BrowserManager.start()`

- Launches Chromium via Playwright (headless = False by default)
- Creates a browser context and opens a new page
- Returns the `Page` object used by all browser services

---

## Step 2 — Login (Two-Step SSO)

**File:** `browser/login_service.py` → `LoginService.login()`

**Step 2a — Navigate**
- Goes to `AMS360_URL` (Vertafore SSO login page)
- Checks if already logged in by waiting for `networkidle` and checking if the email input is absent
- If already logged in → navigates to `AMS360_URL_IF_LOGIN` and skips to Step 3

**Step 2b — Email (Step 1 of SSO)**
- Waits for `#identifierInput`
- Fills the email from `AMS360_USERNAME`
- Clicks `#postButton`

**Step 2c — Password (Step 2 of SSO)**
- Waits for `#password` to appear
- Fills the password from `AMS360_PASSWORD`
- Clicks `[title='Log In']`
- Waits for `networkidle` + 30 seconds for the dashboard to fully load

---

## Step 3 — Navigate to Customer

**File:** `browser/customer_service.py` → `CustomerService.search(customer_name)`

- Waits for the browser to land on `/Home` after login redirect settles
- Waits for `networkidle`
- Navigates to `CUSTOMER_URL` (e.g. `https://www.ams360.com/.../Customer`)
- Waits for the search input `#search-text` to appear
- Types the customer name and presses Enter
- Waits for `.summary-body` to confirm the customer detail page has loaded
- Reads the address from `.summary-body` and compares with the expected address from settings
- If address does not match → logs a warning and returns `False` (workflow stops)
- If address matches → returns `True`

---

## Step 4 — Click Policy Link

**File:** `browser/policy_service.py` → `PolicyService.click_policy()`

- Locates the first `a.policy.launchPolicy.link` element on the customer detail page
- Clicks it
- This triggers AMS360 to open a native Windows desktop window
- Returns `True` if found and clicked, `False` if no link is present

---

## Step 5 — Attach Desktop Window

**File:** `desktop/desktop_manager.py` → `DesktopManager`

**Step 5a — Wait**
- `wait_window("Policy")` — polls every 1 second until a window matching the title pattern `Policy` appears on screen
- Timeout: 30 seconds

**Step 5b — Attach**
- `attach("Policy")` — connects pywinauto to the window using `Application(backend="uia").connect()`
- Returns a `WindowSpecification` object used by all subsequent desktop operations

**Step 5c — Maximize**
- `maximize(attached_window)` — maximizes the window so all controls are visible and accessible

---

## Step 6 — Add Transaction Fee

**File:** `desktop/policy_window.py` → `PolicyWindow.add_transaction_fee(charge_type, amount)`

The values come from `excel/excel_service.py → ExcelService.get_fee_info()` which reads `FEE_CHARGE_TYPE` and `FEE_AMOUNT` from `config/.env`.

**Step 6a — Click New**
- Finds the Transaction Fees section pane (`sctPolicy_PolPremNonPrem_PolFeesTax`)
- Clicks the `New` Hyperlink inside it using `.invoke()`

**Step 6b — Wait 10 seconds**
- Waits for the edit form (`Dialog` pane) to appear inside the fees section

**Step 6c — Set Charge Type**
- Finds `cmbPolicy_PolPremNonPrem_PolFeesTax_PolCmbFeesTaxChargeType` (ComboBox)
- Calls `.select(charge_type)` to choose the value (e.g. "Agency Fee")

**Step 6d — Set Amount**
- Finds `txtPolicy_PolPremNonPrem_PolFeesTax_PolTPPremium` (Edit)
- Calls `.set_text(amount)` to enter the value (e.g. "10.00")

**Step 6e — Wait 10 seconds**

**Step 6f — Click Cancel**
- Clicks the `Cancel` Hyperlink in the fees pane to discard the new row without saving

---

## Step 7 — Read Policy Data

**File:** `desktop/reader.py` → `PolicyReader.read()`

Reads data from the attached window:

| Field | Source |
|---|---|
| Policy Number | Parsed from window title (e.g. `ACI04B11019405`) |
| Effective Date | Parsed from window title (e.g. `7/20/2026`) |
| Expiration Date | Parsed from window title (e.g. `7/20/2027`) |
| Premium | Edit control `txtPolicy_PolPremNonPrem_PolTPPolPremium` |
| Fees & Taxes | Edit control `txtPolicy_PolPremNonPrem_PolTPPolFeesTaxes` |
| Annualized Premium | Edit control `txtPolicy_PolPremNonPrem_PolTPPolAnnualizedPremium` |
| Bill Method | ComboBox `cmbPolicy_PolPremNonPrem_PolInvoicing_PolCmbInvoicingBillmethod` |
| Customer Name | Set from `CustomerInfo.name` |
| Customer Address | Set from `CustomerInfo.address` |

Returns a `PolicyInfo` dataclass instance.

---

## Step 8 — Close Desktop Window

**File:** `desktop/desktop_manager.py` → `DesktopManager.close()`

- Waits `WINDOW_CLOSE_WAIT` seconds (default 30) before closing
- Calls `window.close()`
- Clears the internal `_window` and `_app` references

---

## Step 9 — Write to Excel

**File:** `excel/excel_service.py` → `ExcelService.write_policy(policy_info)`

- Opens `output.xlsx` if it exists, or creates a new workbook with headers
- Appends the `PolicyInfo` data as a new row
- Headers: Policy Number, Effective Date, Expiration Date, Premium, Status, Fees, Annualized Premium, Bill Method, Customer Name, Customer Address
- Saves the file

---

## Step 10 — Stop Browser

**File:** `browser/browser_manager.py` → `BrowserManager.stop()`

- Runs in the `finally` block — always executes even if an earlier step fails
- Closes the browser context and stops Playwright

---

## Configuration

All runtime values are in `config/.env`:

| Key | Purpose |
|---|---|
| `AMS360_URL` | SSO login page URL |
| `AMS360_URL_IF_LOGIN` | URL to navigate to if session is already active |
| `AMS360_USERNAME` | Login email |
| `AMS360_PASSWORD` | Login password |
| `AGENCY` | Agency code |
| `CUSTOMER_NAME` | Customer to search |
| `CUSTOMER_ADDRESS` | Address to verify against the customer page |
| `CUSTOMER_URL` | Direct URL to the Customer search page |
| `OUTPUT_EXCEL` | Output Excel file path |
| `FEE_CHARGE_TYPE` | Charge Type value to select in the fee form |
| `FEE_AMOUNT` | Amount to enter in the fee form |

---

## Error Handling

- Every browser service catches `PlaywrightTimeoutError`, saves a screenshot to `screenshots/`, logs the error, and re-raises
- The workflow catches all exceptions, logs them, and guarantees `BrowserManager.stop()` runs in `finally`
- Logs are written to `logs/ams360.log` with timestamps and the source filename

---

## Pending / Not Yet Implemented

- **Receipt Flow** — click a policy row → Action button → Receipt → Receipt desktop window
- **Excel Input Loop** — read customer rows from an input Excel file instead of `.env`
- **Address Match** — currently commented out in workflow; planned to be re-enabled
