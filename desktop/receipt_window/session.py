from __future__ import annotations

from pywinauto.base_wrapper import BaseWrapper

from helpers.logger import get_logger

logger = get_logger(__name__)


class ReceiptWindowSession:
    """
    Entry point for all operations inside the AMS360 Receipt desktop window.
    Logic to be implemented once the window is observed.
    """

    def __init__(self, window: BaseWrapper):
        self.window = window

    def run(self) -> None:
        logger.info(f"Receipt window opened: {self.window.window_text()}")
        # TODO: implement receipt window logic here
