from __future__ import annotations

import time

from pywinauto import Application, Desktop
from pywinauto.base_wrapper import BaseWrapper
from pywinauto.timings import TimeoutError as PywinautoTimeoutError

from config.constants import TIMEOUTS
from helpers.logger import get_logger

logger = get_logger(__name__)


class DesktopManager:
    def __init__(self):
        self._app: Application | None = None
        self._window: BaseWrapper | None = None

    def wait_window(self, title_re: str, timeout: int = TIMEOUTS.POLICY_WINDOW) -> BaseWrapper:
        logger.info(f"Waiting for window matching: '{title_re}'")
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                windows = Desktop(backend="uia").windows(title_re=title_re, visible_only=True)
                if windows:
                    logger.info(f"Window found: {windows[0].window_text()}")
                    return windows[0]
            except Exception:
                pass
            time.sleep(1)
        raise TimeoutError(f"Window '{title_re}' did not appear within {timeout}s")

    def attach(self, title_re: str) -> BaseWrapper:
        logger.info(f"Attaching to window: '{title_re}'")
        self._app = Application(backend="uia").connect(title_re=title_re)
        self._window = self._app.window(title_re=title_re)
        logger.info("Window attached")
        return self._window

    def maximize(self, window: BaseWrapper | None = None) -> None:
        win = window or self._window
        if win is None:
            raise RuntimeError("No window to maximize")
        win.maximize()
        logger.info("Window maximized")

    def close(self, window: BaseWrapper | None = None) -> None:
        win = window or self._window
        if win is None:
            return
        try:
            logger.info(f"Waiting {TIMEOUTS.WINDOW_CLOSE_WAIT}s before closing window")
            time.sleep(TIMEOUTS.WINDOW_CLOSE_WAIT)
            win.close()
            logger.info("Window closed")
        except Exception as e:
            logger.warning(f"Error closing window: {e}")
        finally:
            self._window = self._app = None
