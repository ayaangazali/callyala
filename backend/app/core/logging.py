"""Structured logging with request context."""

import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Optional

# Request ID context variable
request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def get_request_id() -> str:
    """Get current request ID or generate one."""
    rid = request_id_ctx.get()
    if rid is None:
        rid = str(uuid.uuid4())[:8]
        request_id_ctx.set(rid)
    return rid


class RequestIdFilter(logging.Filter):
    """Add request_id to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get() or "--------"
        return True


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure structured logging."""
    logger = logging.getLogger("voice_ops")
    
    if logger.handlers:
        return logger
    
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(RequestIdFilter())
    
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(request_id)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False
    
    return logger


# Default logger instance
logger = setup_logging()
