import logging
import sys
from datetime import datetime
from pathlib import Path
from config.constants import LOG_FILE, LOGS_DIR

_run_marked = False


def get_logger(name: str) -> logging.Logger:
    global _run_marked
    Path(LOGS_DIR).mkdir(exist_ok=True)

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter("%(asctime)s  %(levelname)-8s  %(filename)s  %(message)s", datefmt="%H:%M:%S")

    if not _run_marked:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write(f"RUN START: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n")
        _run_marked = True

    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger
