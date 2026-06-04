"""Logging tập trung: console + file (app.log, error.log)."""

from __future__ import annotations

import logging
import os
import sys
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

_ROOT_NAME = "foodchat"
_CONFIGURED = False

_BASE_DIR = Path(__file__).resolve().parent.parent
_DEFAULT_LOG_DIR = _BASE_DIR / "logs"


def setup_logging() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    log_dir = Path(os.getenv("LOG_DIR", str(_DEFAULT_LOG_DIR)))
    log_dir.mkdir(parents=True, exist_ok=True)

    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root = logging.getLogger(_ROOT_NAME)
    root.setLevel(level)
    root.propagate = False

    console = logging.StreamHandler(sys.stderr)
    console.setLevel(level)
    console.setFormatter(fmt)
    root.addHandler(console)

    app_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=int(os.getenv("LOG_MAX_BYTES", 2_000_000)),
        backupCount=int(os.getenv("LOG_BACKUP_COUNT", 5)),
        encoding="utf-8",
    )
    app_handler.setLevel(level)
    app_handler.setFormatter(fmt)
    root.addHandler(app_handler)

    error_handler = RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=int(os.getenv("LOG_MAX_BYTES", 2_000_000)),
        backupCount=int(os.getenv("LOG_BACKUP_COUNT", 5)),
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(fmt)
    root.addHandler(error_handler)

    _CONFIGURED = True
    root.info("Logging initialized → %s", log_dir)


def get_logger(module: str) -> logging.Logger:
    setup_logging()
    return logging.getLogger(f"{_ROOT_NAME}.{module}")


def log_exception(
    logger: logging.Logger,
    message: str,
    exc: BaseException,
    **context: Any,
) -> None:
    """Ghi exception đầy đủ stack trace + context vào error.log."""
    ctx = " | ".join(f"{k}={v}" for k, v in context.items() if v is not None)
    full_msg = f"{message} | {ctx}" if ctx else message
    logger.error("%s\n%s", full_msg, traceback.format_exc())


def exception_summary(exc: BaseException, max_len: int = 300) -> str:
    """Chuỗi ngắn để log, không đẩy ra chat."""
    text = f"{type(exc).__name__}: {exc}"
    return text if len(text) <= max_len else text[: max_len - 3] + "..."
