"""
Shared FastAPI dependencies.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from uuid import UUID

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import RateLimitException
from app.core.config import get_settings
from app.core.redis import get_redis as _get_redis_client
from app.core.security import decode_access_token
from app.db.session import get_sessionmaker
from app.models.user import User

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """One database session per request. Service layer commits explicitly."""
    session_factory = get_sessionmaker()
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ---------------------------------------------------------------------------
# Redis
# ---------------------------------------------------------------------------

async def get_redis() -> Redis:
    """Return the shared Redis client."""
    return _get_redis_client()


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,   # allows optional auth (token=None when absent)
)


async def get_current_user(
    token: str | None = Depends(_oauth2_scheme),
    session: AsyncSession = Depends(get_db),
) -> User:
    """
    Require a valid JWT. Raises 401 if token is missing or invalid.
    Use this dependency on routes that require authentication.
    """
    from fastapi import HTTPException, status
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id_str = decode_access_token(token)

    from app.repositories.user import UserRepository
    repo = UserRepository(session)
    user = await repo.get_by_id(UUID(user_id_str))
    if user is None or not user.is_active:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_optional_user(
    token: str | None = Depends(_oauth2_scheme),
    session: AsyncSession = Depends(get_db),
) -> User | None:
    """
    Optional JWT auth. Returns the User if a valid token is present,
    or None for unauthenticated requests.
    Use this on routes that work both anonymously and authenticated.
    """
    if token is None:
        return None
    try:
        user_id_str = decode_access_token(token)
        from app.repositories.user import UserRepository
        repo = UserRepository(session)
        user = await repo.get_by_id(UUID(user_id_str))
        if user and user.is_active:
            return user
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Rate limiting (Redis fixed-window counter)
# ---------------------------------------------------------------------------

async def _check_rate_limit(
    request: Request,
    redis: Redis,
    limit: int,
    window_seconds: int,
    key_suffix: str,
) -> None:
    settings = get_settings()
    if not settings.rate_limit_enabled:
        return

    client_ip = request.client.host if request.client else "unknown"
    key = f"ratelimit:{key_suffix}:{client_ip}"

    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, window_seconds)

    if count > limit:
        raise RateLimitException()


async def rate_limit_create(
    request: Request,
    redis: Redis = Depends(get_redis),
) -> None:
    """60 URL creations per minute per IP."""
    settings = get_settings()
    await _check_rate_limit(
        request,
        redis=redis,
        limit=settings.rate_limit_create_per_minute,
        window_seconds=60,
        key_suffix="create",
    )


async def rate_limit_redirect(
    request: Request,
    redis: Redis = Depends(get_redis),
) -> None:
    """600 redirect requests per minute per IP."""
    settings = get_settings()
    await _check_rate_limit(
        request,
        redis=redis,
        limit=settings.rate_limit_redirect_per_minute,
        window_seconds=60,
        key_suffix="redirect",
    )