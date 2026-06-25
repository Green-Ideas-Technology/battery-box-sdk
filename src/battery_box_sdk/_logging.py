"""Internal diagnostic logging setup — not part of the public API."""

from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path

_LOG_FILENAME = "battery_box_sdk.log"
_MAX_BYTES = 1_048_576  # 1 MB per file
_BACKUP_COUNT = 5


def _setup_file_logging(log_dir: str) -> None:
    """Attach a RotatingFileHandler to the battery_box_sdk logger.

    Called automatically by BatteryBoxClient on instantiation.
    Safe to call multiple times — duplicate handlers are not added.
    """
    logger = logging.getLogger("battery_box_sdk")
    if any(isinstance(h, logging.handlers.RotatingFileHandler) for h in logger.handlers):
        return

    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    handler = logging.handlers.RotatingFileHandler(
        log_path / _LOG_FILENAME,
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
