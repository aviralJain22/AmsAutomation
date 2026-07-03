from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError

from config.constants import SELECTORS, TIMEOUTS
from typing import Literal
from helpers.logger import get_logger
from helpers.screenshot import save_screenshot

logger = get_logger(__name__)


@dataclass
class PolicyRow:
    """Parsed data from a single ExtJS grid row, plus its live Playwright locator."""
    policy_number: str
    effective_date: str   # raw text from grid, e.g. "01/01/2024"
    expiration_date: str  # raw text from grid, e.g. "01/01/2025"
    locator: Locator      # points to the div.x-grid3-row element

    def matches(
        self,
        policy_number: str,
        effective_date: str,
        expiration_date: str,
    ) -> bool:
        return (
            self.policy_number == policy_number.strip()
            and self.effective_date == effective_date.strip()
            and self.expiration_date == expiration_date.strip()
        )


class PolicyGrid:
    """
    Reads and searches the ExtJS policy grid on the AMS360 customer detail page.

    The page can host more than one x-grid3 widget, so rows are scoped to the
    viewport whose header row contains the "Policy" column
    (div.x-grid3-viewport:has(.x-grid3-hd-Policy)) rather than a bare
    "div.x-grid3-row" query, which would also pick up unrelated grids:

        div.x-grid3-viewport
          div.x-grid3-header            ← identifies the grid (has .x-grid3-hd-Policy)
          div.x-grid3-body
            div.x-grid3-row             ← the rows we fetch
              td.x-grid3-td-Policy  →  a  (policy number link)
              td.x-grid3-td-Term    →  line 0: effective date, line 1: expiration date
    """

    def __init__(self, page: Page) -> None:
        self.page = page

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_all_rows(self) -> list[PolicyRow]:
        """
        Fetches every row from the grid and returns parsed PolicyRow objects.
        Rows that fail to parse (e.g. missing columns) are skipped with a warning.
        """
        row_locators = self.page.locator(SELECTORS.POLICY_GRID_ROW)
        count = row_locators.count()
        logger.info(f"Policy grid: {count} row(s) found")

        rows: list[PolicyRow] = []
        for i in range(count):
            row = row_locators.nth(i)
            parsed = self._parse_row(row, index=i)
            if parsed is not None:
                rows.append(parsed)

        self._log_rows(rows)
        return rows

    def find_row(
        self,
        policy_number: str,
        effective_date: str,
        expiration_date: str,
    ) -> Optional[PolicyRow]:
        """
        Returns the first PolicyRow whose policy_number, effective_date, and
        expiration_date all match the supplied values (stripped, exact match).
        Returns None if no match is found.
        """
        rows = self.get_all_rows()
        for row in rows:
            if row.matches(policy_number, effective_date, expiration_date):
                logger.info(
                    f"Matched policy {policy_number!r} "
                    f"({effective_date} – {expiration_date})"
                )
                return row

        logger.warning(
            f"No grid row matched policy {policy_number!r} "
            f"({effective_date} – {expiration_date})"
        )
        return None

    def select_row(
        self,
        policy_number: str,
        effective_date: str,
        expiration_date: str,
    ) -> Optional[PolicyRow]:
        """
        Clicks the matching row to select it in the grid (does not follow the
        policy link).  Returns the PolicyRow on success, None if not found.
        """
        row = self.find_row(policy_number, effective_date, expiration_date)
        if row is None:
            return None

        try:
            row.locator.click(timeout=TIMEOUTS.DEFAULT)
            logger.info(f"Selected grid row for policy {policy_number!r}")
            return row
        except PlaywrightTimeoutError as e:
            save_screenshot(self.page, "policy_grid_select_failed")
            logger.error(f"Failed to select grid row for {policy_number!r}: {e}")
            raise

    def perform_action(
        self,
        policy_number: str,
        effective_date: str,
        expiration_date: str,
        action: Literal["Renew", "Endorse"],
    ) -> bool:
        """
        Selects the matching row, then clicks the Renew or Endorse toolbar button.
        Returns True on success, False if the row was not found.
        """
        row = self.select_row(policy_number, effective_date, expiration_date)
        if row is None:
            return False

        if action == "Renew":
            selector = SELECTORS.RENEW_BUTTON
        elif action == "Endorse":
            selector = SELECTORS.ENDORSE_BUTTON
        else:
            raise ValueError(f"Unsupported action: {action!r}")
        
        label = f"policy_grid_{action.lower()}_failed"

        try:
            self.page.locator(selector).click(timeout=TIMEOUTS.DEFAULT)
            logger.info(f"Clicked '{action}' button for policy {policy_number!r}")
            return True
        except PlaywrightTimeoutError as e:
            save_screenshot(self.page, label)
            logger.error(f"'{action}' button click failed for {policy_number!r}: {e}")
            raise

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _log_rows(self, rows: list[PolicyRow]) -> None:
        sep   = "-" * 64
        col_w = 20
        header = f"{'Policy Number':<{col_w}}{'Effective Date':<{col_w}}{'Expiry Date':<{col_w}}"
        lines = [
            "",
            sep,
            "Policy Data".center(64),
            sep,
            header,
            "-" * col_w * 3,
        ]
        for r in rows:
            lines.append(
                f"{r.policy_number:<{col_w}}{r.effective_date:<{col_w}}{r.expiration_date:<{col_w}}"
            )
        lines.append(sep)
        logger.info("\n".join(lines))

    def _parse_row(self, row: Locator, *, index: int) -> Optional[PolicyRow]:
        """
        Extracts policy number and term dates from a single grid row locator.
        Returns None and logs a warning if any required element is missing.
        """
        try:
            policy_number = (
                row.locator(SELECTORS.POLICY_GRID_POLICY_NUMBER)
                .inner_text(timeout=TIMEOUTS.DEFAULT)
                .strip()
            )

            term_cell_text = (
                row.locator(SELECTORS.POLICY_GRID_TERM_CELL)
                .inner_text(timeout=TIMEOUTS.DEFAULT)
                .strip()
            )

            # Term cell contains two lines: effective date \n expiration date
            lines = [ln.strip() for ln in term_cell_text.splitlines() if ln.strip()]
            if len(lines) < 2:
                logger.warning(
                    f"Row {index}: term cell has fewer than 2 lines — skipping. "
                    f"Raw text: {term_cell_text!r}"
                )
                return None

            effective_date, expiration_date = lines[0], lines[1]

            return PolicyRow(
                policy_number=policy_number,
                effective_date=effective_date,
                expiration_date=expiration_date,
                locator=row,
            )

        except PlaywrightTimeoutError:
            logger.warning(f"Row {index}: timed out reading cell — skipping")
            return None
        except Exception as exc:
            logger.warning(f"Row {index}: unexpected parse error — skipping. {exc}")
            return None
