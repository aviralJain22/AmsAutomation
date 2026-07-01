from __future__ import annotations

import time
from pathlib import Path
from typing import TYPE_CHECKING

from config.constants import SCREENSHOTS_DIR
from helpers.logger import get_logger

if TYPE_CHECKING:
    from playwright.sync_api import Page

logger = get_logger(__name__)


def save_screenshot(page: "Page", label: str) -> str:
    Path(SCREENSHOTS_DIR).mkdir(exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    path = f"{SCREENSHOTS_DIR}/{timestamp}_{label}.png"
    try:
        page.screenshot(path=path)
        logger.info(f"Screenshot saved: {path}")
    except Exception as e:
        logger.warning(f"Could not save screenshot '{label}': {e}")
    return path
