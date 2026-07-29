"""
URL service — business logic layer.

Responsibilities:
- Short code generation with collision retry.
- Cache-aside reads (Redis → DB → cache populate).
- Expiration enforcement.
- Delegating DB writes to URLRepository.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import (
    BadRequestException,
    ConflictException,
    GoneException,
    NotFoundException,
)
from app.core.config import get_settings
from app.core.logging import get_logger
from app.repositories.url import URLRepository
from app.utils.short_code import generate_short_code

log = get_logger(__name__)

_MAX_COLLISION_RETRIES = 5
_CACHE_PREFIX = "url:"


class URLService:
    def __init__(self, session: AsyncSession, redis: Redis) -> None:
        self._repo = URLRepository(session)
        self._session = session
        self._redis = redis
        self._settings = get_settings()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def create(
        self,
        *,
        long_url: str,
        custom_alias: str | None = None,
        expiration_date: datetime | None = None,
        owner_id: UUID | None = None,
    ) -> dict:
        short_code = await self._resolve_short_code(custom_alias)

        url = await self._repo.create(
            original_url=long_url,
            short_code=short_code,
            expires_at=expiration_date,
            owner_id=owner_id,
        )
        await self._session.commit()

        log.info("url.created", short_code=short_code, long_url=long_url)

        return {
            "short_url": self._build_short_url(short_code),
            "alias": short_code,
            "expires_at": url.expires_at,
        }

    async def resolve(self, short_code: str) -> str:
        """Return the original URL for a short code, enforcing expiration."""
        cache_key = f"{_CACHE_PREFIX}{short_code}"

        # Cache hit
        cached = await self._redis.get(cache_key)
        if cached:
            await self._repo.increment_click_count(short_code)
            await self._session.commit()
            return cached

        # DB lookup
        url = await self._repo.get_by_short_code(short_code)
        if url is None:
            raise NotFoundException(f"Short code '{short_code}' not found.")

        if not url.is_active:
            raise GoneException(f"Short code '{short_code}' is no longer active.")

        if url.expires_at and url.expires_at < datetime.now(UTC):
            raise GoneException(f"Short code '{short_code}' has expired.")

        # Populate cache
        ttl = self._compute_ttl(url.expires_at)
        await self._redis.set(cache_key, url.original_url, ex=ttl)

        # Increment clicks
        await self._repo.increment_click_count(short_code)
        await self._session.commit()

        return url.original_url

    async def get_metadata(self, short_code: str) -> dict:
        """Return metadata about a short URL (non-redirecting)."""
        url = await self._repo.get_by_short_code(short_code)
        if url is None:
            raise NotFoundException(f"Short code '{short_code}' not found.")

        return {
            "short_url": self._build_short_url(short_code),
            "long_url": url.original_url,
            "created_at": url.created_at,
            "expires_at": url.expires_at,
            "clicks": url.click_count,
        }

    async def delete(self, short_code: str) -> None:
        """Delete a short URL and evict from cache."""
        deleted = await self._repo.delete_by_short_code(short_code)
        if not deleted:
            raise NotFoundException(f"Short code '{short_code}' not found.")

        await self._session.commit()
        await self._redis.delete(f"{_CACHE_PREFIX}{short_code}")
        log.info("url.deleted", short_code=short_code)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    async def _resolve_short_code(self, custom_alias: str | None) -> str:
        if custom_alias:
            if await self._repo.short_code_exists(custom_alias):
                raise ConflictException(
                    f"Custom alias '{custom_alias}' is already in use."
                )
            return custom_alias

        for attempt in range(1, _MAX_COLLISION_RETRIES + 1):
            code = generate_short_code(self._settings.short_code_length)
            if not await self._repo.short_code_exists(code):
                return code
            log.warning("url.short_code_collision", attempt=attempt, code=code)

        raise BadRequestException(
            "Could not generate a unique short code. Please try again."
        )

    def _build_short_url(self, short_code: str) -> str:
        return f"{self._settings.base_url.rstrip('/')}/{short_code}"

    def _compute_ttl(self, expires_at: datetime | None) -> int:
        """TTL in seconds for Redis. Falls back to config default."""
        if expires_at is None:
            return self._settings.cache_ttl_seconds
        remaining = int((expires_at - datetime.now(UTC)).total_seconds())
        return max(1, min(remaining, self._settings.cache_ttl_seconds))
