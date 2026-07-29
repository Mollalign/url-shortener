"""
Async Redis client lifecycle.
"""

from __future__ import annotations

from redis.asyncio import ConnectionPool, Redis

from app.core.config import get_settings
from app.core.logging import get_logger

log = get_logger(__name__)


_pool: ConnectionPool | None = None
_client: Redis | None = None


def init_redis() -> Redis:
    """Create the global Redis client. Called from lifespan startup."""
    global _pool, _client
    if _client is not None:
        return _client

    settings = get_settings()
    _pool = ConnectionPool.from_url(
        settings.redis_url,
        max_connections=settings.redis_max_connections,
        decode_responses=True,
    )
    _client = Redis(connection_pool=_pool)
    log.info("redis.client_initialized", url=settings.redis_url)
    return _client


async def dispose_redis() -> None:
    """Close Redis connections. Called from lifespan shutdown."""
    global _pool, _client
    if _client is not None:
        await _client.aclose()
        log.info("redis.client_disposed")
    if _pool is not None:
        await _pool.aclose()
    _client = None
    _pool = None


def get_redis() -> Redis:
    if _client is None:
        raise RuntimeError("Redis client not initialized — call init_redis() first.")
    return _client


async def redis_healthcheck() -> bool:
    """Lightweight check used by the /health endpoint."""
    try:
        client = get_redis()
        return bool(await client.ping())
    except Exception as exc:  # noqa: BLE001
        log.warning("redis.healthcheck_failed", error=str(exc))
        return False
