"""Logging tập trung: console + file (app.log, error.log)."""

from __future__ import annotations

import contextvars
import logging
import os
import sys
import traceback
import uuid
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

_ROOT_NAME = "foodchat"
_CONFIGURED = False

_BASE_DIR = Path(__file__).resolve().parent.parent
_DEFAULT_LOG_DIR = _BASE_DIR / "logs"

_request_id: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")


class _RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = _request_id.get()
        return True


def set_request_id(request_id: str | None = None) -> str:
    rid = request_id or uuid.uuid4().hex[:8]
    _request_id.set(rid)
    return rid


def get_request_id() -> str:
    return _request_id.get()


def clear_request_id() -> None:
    _request_id.set("-")


def setup_logging() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    log_dir = Path(os.getenv("LOG_DIR", str(_DEFAULT_LOG_DIR)))
    log_dir.mkdir(parents=True, exist_ok=True)

    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(request_id)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    req_filter = _RequestIdFilter()

    root = logging.getLogger(_ROOT_NAME)
    root.setLevel(level)
    root.propagate = False

    console = logging.StreamHandler(sys.stderr)
    console.setLevel(level)
    console.setFormatter(fmt)
    console.addFilter(req_filter)
    root.addHandler(console)

    app_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=int(os.getenv("LOG_MAX_BYTES", 2_000_000)),
        backupCount=int(os.getenv("LOG_BACKUP_COUNT", 5)),
        encoding="utf-8",
    )
    app_handler.setLevel(level)
    app_handler.setFormatter(fmt)
    app_handler.addFilter(req_filter)
    root.addHandler(app_handler)

    error_handler = RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=int(os.getenv("LOG_MAX_BYTES", 2_000_000)),
        backupCount=int(os.getenv("LOG_BACKUP_COUNT", 5)),
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(fmt)
    error_handler.addFilter(req_filter)
    root.addHandler(error_handler)

    _CONFIGURED = True
    root.info("Logging initialized → %s | level=%s", log_dir, level_name)


def get_logger(module: str) -> logging.Logger:
    setup_logging()
    return logging.getLogger(f"{_ROOT_NAME}.{module}")


def format_context(**context: Any) -> str:
    parts: list[str] = []
    for key, value in context.items():
        if value is None:
            continue
        if isinstance(value, float):
            parts.append(f"{key}={value:.6f}")
        elif isinstance(value, str) and len(value) > 160:
            parts.append(f'{key}="{value[:157]}..."')
        else:
            parts.append(f"{key}={value}")
    return " | ".join(parts)


def log_event(
    logger: logging.Logger,
    message: str,
    level: int = logging.INFO,
    **context: Any,
) -> None:
    ctx = format_context(**context)
    full = f"{message} | {ctx}" if ctx else message
    logger.log(level, full)


def log_location(logger: logging.Logger, label: str, lat: float | None, lng: float | None) -> None:
    if lat is None or lng is None:
        log_event(logger, label, location="missing")
        return
    log_event(logger, label, lat=lat, lng=lng)


def log_restaurants(
    logger: logging.Logger,
    label: str,
    restaurants: list[dict],
    *,
    level: int = logging.INFO,
) -> None:
    log_event(logger, label, level=level, count=len(restaurants))
    for idx, r in enumerate(restaurants, start=1):
        log_event(
            logger,
            f"{label} #{idx}",
            level=level,
            name=r.get("name"),
            place_id=r.get("place_id"),
            lat=r.get("lat"),
            lng=r.get("lng"),
            distance_km=r.get("distance_km"),
            score=r.get("score"),
        )


def log_exception(
    logger: logging.Logger,
    message: str,
    exc: BaseException,
    **context: Any,
) -> None:
    """Ghi exception đầy đủ stack trace + context vào error.log."""
    ctx = format_context(**context)
    full_msg = f"{message} | {ctx}" if ctx else message
    logger.error("%s\n%s", full_msg, traceback.format_exc())


def exception_summary(exc: BaseException, max_len: int = 300) -> str:
    """Chuỗi ngắn để log, không đẩy ra chat."""
    text = f"{type(exc).__name__}: {exc}"
    return text if len(text) <= max_len else text[: max_len - 3] + "..."
