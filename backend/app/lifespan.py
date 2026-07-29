"""
FastAPI lifespan.

Startup:
- Configure logging (must run first so subsequent steps emit structured logs).
- Initialize the DB engine + sessionmaker.
- Initialize the Redis client.
- Initialize the shared rental-saas HTTP client (connection pool for inbound bridge).
- Dispose Redis pool, then DB engine.
- Order matters: services that depend on DB shut down first.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.logging import configure_logging, get_logger
from app.core.redis import dispose_redis, init_redis
from app.db.session import dispose_engine, init_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    log = get_logger("lifespan")

    log.info("app.starting")
    init_engine()
    init_redis()
    log.info("app.started")

    try:
        yield
    finally:
        log.info("app.stopping")
        await dispose_redis()
        await dispose_engine()
        log.info("app.stopped")
