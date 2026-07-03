from __future__ import annotations

from pywinauto.base_wrapper import BaseWrapper

from desktop.endorse_window.reader import EndorseWindowReader
from helpers.logger import get_logger

logger = get_logger(__name__)


class EndorseWindowSession:
    """
    Single entry point for operations inside the AMS360 Endorsement desktop
    window. Receives an already-attached window.
    """

    def __init__(self, window: BaseWrapper):
        self.window = window
        self._reader = EndorseWindowReader(window)

    def run(self, description: str) -> None:
        self._reader.set_description(description)
