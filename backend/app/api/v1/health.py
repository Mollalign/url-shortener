"""
Liveness & readiness probes.

`/health` is unauthenticated and cheap (returns shortly even if DB is slow).
`/health/ready` performs DB + Redis pings — used by orchestrators / k8s.
"""

from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from app.common.response import HealthResponse
from app.core.config import get_settings
from app.core.redis import redis_healthcheck
from app.db.session import get_sessionmaker

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse, summary="Liveness probe")
async def liveness() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        environment=settings.environment,
        version="0.1.0",
        db=True,
        redis=True,
    )


@router.get("/ready", response_model=HealthResponse, summary="Readiness probe")
async def readiness() -> HealthResponse:
    settings = get_settings()

    db_ok = False
    try:
        sm = get_sessionmaker()
        async with sm() as session:
            await session.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    redis_ok = await redis_healthcheck()

    return HealthResponse(
        status="ok" if db_ok and redis_ok else "degraded",
        environment=settings.environment,
        version="0.1.0",
        db=db_ok,
        redis=redis_ok,
    )
