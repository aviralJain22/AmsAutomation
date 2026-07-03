# AMS360 Automation — Grid-Aware Flow (v2)

## Overview

This document describes the updated automation flow that introduces grid-aware policy matching and configurable action execution (Renew or Endorse).

The key difference from `flow.md` is that instead of clicking the first available policy link, the workflow now:
1. Runs the desktop flow first to read the policy number and dates
2. Matches those values against the ExtJS policy grid
3. Selects the correct row and clicks the action button (Renew or Endorse) specified in the input

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
- Navigates to `CUSTOMER_URL`
- Waits for the search input `#search-text` to appear
- Types the customer name and presses Enter
- Waits for `.summary-body` to confirm the customer detail page has loaded

---

## Step 4 — Desktop Policy Flow

**File:** `desktop/orchestrator.py` → `DesktopOrchestrator.run_policy_flow(customer, fee)`

The desktop flow runs before the grid action because the policy number and dates read from the desktop window are what the grid match depends on.

**Step 4a — Wait & Attach Window**
- **File:** `desktop/desktop_manager.py` → `DesktopManager.wait_window("Policy")`
- Polls every 1 second until a window matching the title pattern `Policy` appears
- Timeout: 30 seconds
- Then calls `attach("Policy")` using `Application(backend="uia").connect()` and maximizes the window

**Step 4b — Open Basic Policy Info & Set Status**
- **File:** `desktop/policy_window/basic_info.py` → `BasicInfo.open()` + `set_status()`
- Expands the Basic Policy Information section
- Calls `PolicyReader.get_period()` to determine if the policy term is Annual or Short-Period
- Sets the Status field accordingly: `Active` for Annual, `Non-renewed` for Short-Period

**Step 4c — Demo Fee Entry (no save)**
- **File:** `desktop/policy_window/fee_handler.py` → `FeeHandler.add(charge_type, amount)`
- Clicks `New` in the Transaction Fees pane to open the add-fee form
- Sets the Charge Type (`FEE_CHARGE_TYPE`) and Amount (`FEE_AMOUNT`)
- Clicks `Cancel` — the fee is not saved; this step is a demonstration only

**Step 4d — Read Policy Fields**
- **File:** `desktop/policy_window/reader.py` → `PolicyReader.read()`
- Parses the window title to extract policy number, effective date, and expiration date
- Reads Edit and ComboBox controls for premium, fees, annualized premium, and bill method

| Field | Source |
|---|---|
| Policy Number | Parsed from window title |
| Effective Date | Parsed from window title |
| Expiration Date | Parsed from window title |
| Premium | Edit control `txtPolicy_PolPremNonPrem_PolTPPolPremium` |
| Fees & Taxes | Edit control `txtPolicy_PolPremNonPrem_PolTPPolFeesTaxes` |
| Annualized Premium | Edit control `txtPolicy_PolPremNonPrem_PolTPPolAnnualizedPremium` |
| Bill Method | ComboBox `cmbPolicy_PolPremNonPrem_PolInvoicing_PolCmbInvoicingBillmethod` |

Returns a `PolicyInfo` dataclass instance.

**Step 4e — Close Desktop Window**
- **File:** `desktop/desktop_manager.py` → `DesktopManager.close()`
- Waits `WINDOW_CLOSE_WAIT` seconds (default 30) before closing
- Calls `window.close()`

---

## Step 5 — Read Policy Instruction

**File:** `excel/excel_service.py` → `ExcelService.get_policy_instruction()`

- Returns a `PolicyInstruction(action)` dataclass (defined in `excel/models.py`)
- `action` is a `Literal["Renew", "Endorse"]` — specifies which toolbar button to click
- Phase 1: reads `POLICY_ACTION` from `config/.env` (default: `"Renew"`)
- Phase 2: will read per-row from an input Excel file

---

## Step 6 — Find & Match Policy Row in Grid

**File:** `browser/policy_grid.py` → `PolicyGrid`

**Step 6a — Fetch All Rows**
- `get_all_rows()` locates every `div.x-grid3-row` element on the customer detail page
- For each row, calls `_parse_row()` to extract:
  - Policy Number from `td.x-grid3-td-Policy a`
  - Effective Date and Expiration Date from `td.x-grid3-td-Term` (line 0 and line 1)
- Rows that are missing columns or time out are skipped with a `logger.warning`
- Returns a list of `PolicyRow` dataclass objects, each carrying the parsed values and its live Playwright `Locator`

**Step 6b — Match Row**
- `find_row(policy_number, effective_date, expiration_date)` performs a linear scan
- Each `PolicyRow.matches()` compares all three fields with `.strip()` exact matching
- Returns the first matching `PolicyRow`, or `None` if nothing matches
- If no match → `logger.warning` and the workflow stops cleanly

---

## Step 7 — Select Row & Click Action Button

**File:** `browser/policy_grid.py` → `PolicyGrid.perform_action()`  
**File:** `browser/policy_service.py` → `PolicyService.perform_grid_action()`

**Step 7a — Select Row**
- `select_row()` clicks the matched `div.x-grid3-row` element directly (not the `<a>` link inside it)
- This selects the row in the ExtJS grid without navigating away or opening the desktop window

**Step 7b — Click Action Button**
- Reads `instruction.action` from Step 5 to choose the selector:
  - `"Renew"` → clicks `RENEW_BUTTON` (`config/constants.py`)
  - `"Endorse"` → clicks `ENDORSE_BUTTON` (`config/constants.py`)
- On timeout → saves a screenshot and re-raises

> `RENEW_BUTTON` and `ENDORSE_BUTTON` in `config/constants.py` use XPath selectors `//button[normalize-space()='Renew']` and `//button[normalize-space()='Endorse']`.

---

## Step 8 — Write to Excel

**File:** `excel/excel_service.py` → `ExcelService.write_policy(policy_info)`

- Opens `output.xlsx` if it exists, or creates a new workbook with headers
- Appends the `PolicyInfo` data as a new row
- Headers: Policy Number, Effective Date, Expiration Date, Premium, Status, Fees, Annualized Premium, Bill Method, Customer Name, Customer Address
- Saves the file

---

## Step 9 — Stop Browser

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
| `POLICY_ACTION` | Action to perform on the matched row: `Renew` or `Endorse` (default: `Renew`) |

---

## Error Handling

- Every browser service catches `PlaywrightTimeoutError`, saves a screenshot to `screenshots/`, logs the error, and re-raises
- Grid row not found → `logger.warning`, workflow returns cleanly (no exception raised)
- `select_row` timeout → screenshot saved as `policy_grid_select_failed.png`, exception re-raised
- Action button timeout → screenshot saved as `policy_grid_renew_failed.png` or `policy_grid_endorse_failed.png`, exception re-raised
- Malformed grid rows → individually skipped with `logger.warning`; remaining rows are still parsed
- The workflow catches all exceptions, logs them, and guarantees `BrowserManager.stop()` runs in `finally`
- Logs are written to `logs/ams360.log` with timestamps and the source filename

---

## Pending / Not Yet Implemented

- **Excel Input Loop** — see next item (action button XPaths are now confirmed)
- **Excel Input Loop** — `get_customer()`, `get_fee_info()`, and `get_policy_instruction()` all read from `.env`; Phase 2 will loop over rows in an input Excel file
- **Receipt Window** — `desktop/receipt_window/` is a placeholder for Phase 2 receipt automation
