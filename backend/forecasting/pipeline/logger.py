"""
forecasting/pipeline/logger.py
==============================
Lightweight structured logger for the forecasting pipeline.
Writes to stdout (captured by the scheduler) and to a rotating log file.
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path


def get_logger(name: str = "sarimax_pipeline", log_dir: Path | None = None) -> logging.Logger:
    """Return a configured logger.  Call once per pipeline run."""
    logger = logging.getLogger(name)
    if logger.handlers:          # avoid duplicate handlers on re-import
        return logger

    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter(
        fmt="%(asctime)s [%(levelname)-8s] %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # File (rotating by run date)
    if log_dir is not None:
        log_dir.mkdir(parents=True, exist_ok=True)
        day = datetime.now().strftime("%Y-%m-%d")
        fh = logging.FileHandler(log_dir / f"forecast_{day}.log", encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger
