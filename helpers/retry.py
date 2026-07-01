from __future__ import annotations

import functools
import time
from typing import Callable, Type, Tuple

from helpers.logger import get_logger

logger = get_logger(__name__)


def retry(
    attempts: int = 3,
    delay: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
):
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc: Exception | None = None
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    logger.warning(f"{func.__name__} attempt {attempt}/{attempts} failed: {e}")
                    if attempt < attempts:
                        time.sleep(delay)
            raise last_exc
        return wrapper
    return decorator
