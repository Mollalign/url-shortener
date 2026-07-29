"""
URL CRUD endpoints.

POST   /urls              — create a short URL (optional auth — associates owner if JWT present)
GET    /urls/{short_code} — get metadata (non-redirecting)
DELETE /urls/{short_code} — delete a short URL
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_optional_user, get_redis, rate_limit_create
from app.models.user import User
from app.schemas.url import ErrorResponse, URLCreateRequest, URLCreateResponse, URLMetaResponse
from app.services.url import URLService

router = APIRouter(prefix="/urls", tags=["urls"])


def _service(
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> URLService:
    return URLService(session, redis)


@router.post(
    "",
    response_model=URLCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid URL or expiration date"},
        409: {"model": ErrorResponse, "description": "Custom alias already in use"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
    },
    summary="Create a short URL",
    dependencies=[Depends(rate_limit_create)],
)
async def create_url(
    body: URLCreateRequest,
    svc: URLService = Depends(_service),
    current_user: User | None = Depends(get_optional_user),
) -> URLCreateResponse:
    """
    Create a short URL. If a valid JWT is provided the URL is associated
    with the authenticated user and appears in GET /users/me/urls.
    Anonymous creation is also allowed.
    """
    result = await svc.create(
        long_url=str(body.long_url),
        custom_alias=body.custom_alias,
        expiration_date=body.expiration_date,
        owner_id=current_user.id if current_user else None,
    )
    return URLCreateResponse(**result)


@router.get(
    "/{short_code}",
    response_model=URLMetaResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Short code not found"},
    },
    summary="Get URL metadata",
)
async def get_url_metadata(
    short_code: str,
    svc: URLService = Depends(_service),
) -> URLMetaResponse:
    result = await svc.get_metadata(short_code)
    return URLMetaResponse(**result)


@router.delete(
    "/{short_code}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": ErrorResponse, "description": "Short code not found"},
    },
    summary="Delete a short URL",
)
async def delete_url(
    short_code: str,
    svc: URLService = Depends(_service),
) -> None:
    await svc.delete(short_code)
