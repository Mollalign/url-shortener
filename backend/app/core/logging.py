"""
Structured logging configuration using structlog.

Design:
- One configure_logging() call at app startup.
- contextvars-based binding lets us attach `request_id`, `tenant_id`, `user_id`
  to every log line for the duration of a request without threading them
  through function signatures.
- Pretty/dev renderer in development, JSON in production.
- Standard library `logging` is routed through structlog so third-party libs
  (sqlalchemy, uvicorn) get the same processors.
"""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars, merge_contextvars

from app.core.config import get_settings


def _build_processors(json_output: bool) -> list[Any]:
    """Build the structlog processor chain.

    Order matters:
      1. merge_contextvars — pull bound vars (tenant_id, request_id, ...).
      2. add_log_level / add_logger_name — annotate the event.
      3. TimeStamper — add ISO timestamp.
      4. format_exc_info — render exceptions cleanly.
      5. final renderer — JSON or console.
    """
    shared: list[Any] = [
        merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if json_output:
        shared.append(structlog.processors.JSONRenderer())
    else:
        shared.append(structlog.dev.ConsoleRenderer(colors=True))

    return shared


def configure_logging() -> None:
    """Configure both structlog and stdlib logging.

    Safe to call multiple times — subsequent calls overwrite handlers cleanly.
    """
    settings = get_settings()
    use_json = settings.log_json or settings.is_production
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    processors = _build_processors(json_output=use_json)

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.stdlib.LoggerFactory(),
        context_class=dict,
        cache_logger_on_first_use=True,
    )

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=processors[-1],
            foreign_pre_chain=processors[:-1],
        )
    )

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)

    for noisy in ("uvicorn.access", "sqlalchemy.engine.Engine"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Get a bound structlog logger. Always prefer this over logging.getLogger."""
    return structlog.get_logger(name) if name else structlog.get_logger()


__all__ = [
    "bind_contextvars",
    "clear_contextvars",
    "configure_logging",
    "get_logger",
]
