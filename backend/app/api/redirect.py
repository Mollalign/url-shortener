"""
Root-level redirect router.

GET /{short_code} → 302 redirect to original URL
                  → 404 if not found
                  → 410 if expired / deactivated

Mounted at the app root (NOT under /api/v1) so short URLs work at:
    http://localhost:8000/abc123
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_redis, rate_limit_redirect
from app.services.url import URLService

redirect_router = APIRouter(tags=["redirect"])


@redirect_router.get(
    "/{short_code}",
    response_class=RedirectResponse,
    status_code=302,
    summary="Redirect to original URL",
    include_in_schema=True,
    responses={
        302: {"description": "Redirects to the original URL"},
        404: {"description": "Short code not found"},
        410: {"description": "Short code expired or deactivated"},
    },
    dependencies=[Depends(rate_limit_redirect)],
)
async def redirect_to_original(
    short_code: str,
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> RedirectResponse:
    svc = URLService(session, redis)
    original_url = await svc.resolve(short_code)
    return RedirectResponse(url=original_url, status_code=302)
