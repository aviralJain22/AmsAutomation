# AMS360 Automation

Automates AMS360 insurance software to log in, search for a customer, open their policy in the native Windows desktop window, read policy data, and write it to Excel.

---

## Architecture

```
main.py
   │
   ▼
AMS360Workflow
   │
   ├── Browser Layer (Playwright)
   │     ├── BrowserManager      — Playwright lifecycle
   │     ├── LoginService        — navigate, fill credentials, wait for dashboard
   │     ├── CustomerService     — search customer by name
   │     └── PolicyService       — locate and click policy row
   │
   ├── Desktop Layer (pywinauto)
   │     ├── DesktopManager      — attach, maximize, close AMS360 window
   │     └── PolicyReader        — read fields → PolicyInfo
   │
   ├── Excel Layer (openpyxl)
   │     ├── ExcelService        — write PolicyInfo row to output.xlsx
   │     └── PolicyInfo          — dataclass model for policy data
   │
   └── Helpers
         ├── logger.py           — file + console logging
         ├── screenshot.py       — save failure screenshots
         ├── retry.py            — @retry decorator
         └── waits.py            — Playwright wait wrappers
```

---

## Folder Structure

```
WindowInspect/
├── config/
│   ├── .env                 # credentials and runtime config
│   ├── constants.py         # selectors, timeouts, window titles
│   └── settings.py          # pydantic Settings loaded from .env
├── browser/
│   ├── browser_manager.py
│   ├── login_service.py
│   ├── customer_service.py
│   └── policy_service.py
├── desktop/
│   ├── desktop_manager.py
│   └── reader.py
├── excel/
│   ├── models.py
│   └── excel_service.py
├── helpers/
│   ├── logger.py
│   ├── screenshot.py
│   ├── retry.py
│   └── waits.py
├── workflow/
│   └── ams360_workflow.py
├── logs/                    # created at runtime
├── screenshots/             # created at runtime
├── requirements.txt
└── main.py
```

---

## Setup

### 1. Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Configure credentials

Edit `config/.env`:

```env
AMS360_URL=https://www.ams360.com
AMS360_USERNAME=your_username
AMS360_PASSWORD=your_password
CUSTOMER_NAME=Seymour, James M
OUTPUT_EXCEL=output.xlsx
```

### 4. Update browser selectors

Open `config/constants.py` and replace the placeholder CSS selectors with the real ones from the AMS360 web UI. Use browser DevTools to inspect elements.

```python
USERNAME_INPUT: str = "#username"       # update these
PASSWORD_INPUT: str = "#password"
LOGIN_BUTTON:   str = "#loginButton"
# ...
```

### 5. Update desktop control IDs

The AMS360 policy window is a native Windows application. After the window opens, discover its control automation IDs:

```python
from pywinauto import Desktop
windows = Desktop(backend="uia").windows(title_re="Policy")
windows[0].print_control_identifiers()
```

Then update the `auto_id` values in `desktop/reader.py` to match.

---

## Running

```bash
python main.py
```

The workflow:

1. Opens Chromium browser
2. Logs into AMS360
3. Searches for the customer defined in `.env`
4. Clicks the policy row → AMS360 opens a desktop window
5. pywinauto attaches to the window and reads policy fields
6. Closes the window and browser
7. Writes the data to `output.xlsx`

Logs are written to `logs/ams360.log`. Failure screenshots are saved to `screenshots/`.

---

## Output

`output.xlsx` is created (or appended to) with these columns:

| Policy Number | Effective Date | Expiration Date | Premium | Status | Customer |
|---------------|---------------|-----------------|---------|--------|----------|

---

## Phase 2 — Excel Input (planned)

Currently the customer name is read from `.env`. In Phase 2, `ExcelService.get_next_customer()` will read rows from an input Excel file one by one, and the workflow will loop over each customer. Only `excel_service.py` and `workflow/ams360_workflow.py` need to change — all other layers remain the same.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Login times out | Check `AMS360_URL` and credentials in `.env`. Update `SELECTORS` in `constants.py`. |
| Customer search fails | Inspect the AMS360 search page and update `CUSTOMER_SEARCH_INPUT` / `SEARCH_BUTTON` selectors. |
| Desktop window not found | Run `print_control_identifiers()` to confirm the window title matches `WINDOW_TITLES.POLICY_WINDOW`. |
| Policy fields return empty | Update `auto_id` values in `desktop/reader.py` to match the real AMS360 control IDs. |
| `pydantic_settings` import error | Run `pip install pydantic-settings`. |
