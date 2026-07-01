from __future__ import annotations

from datetime import datetime
from dateutil.relativedelta import relativedelta


def parse_policy_date(date_str: str) -> datetime:
    return datetime.strptime(date_str.strip(), "%m/%d/%Y")


def get_policy_period(effective_date: str, expiration_date: str) -> str:
    """Returns 'Annual' if exactly 12 months (±1 day), 'Short-Period' otherwise."""
    try:
        eff = parse_policy_date(effective_date)
        exp = parse_policy_date(expiration_date)
        annual_end = eff + relativedelta(months=12)
        if abs((exp - annual_end).days) <= 1:
            return "Annual"
        return "Short-Period"
    except Exception:
        return "Annual"
