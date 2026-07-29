"""
URL repository — all DB queries for the `urls` table.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.url import URL


class URLRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_short_code(self, short_code: str) -> URL | None:
        result = await self._session.execute(
            select(URL).where(URL.short_code == short_code)
        )
        return result.scalar_one_or_none()

    async def short_code_exists(self, short_code: str) -> bool:
        result = await self._session.execute(
            select(URL.id).where(URL.short_code == short_code).limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def create(
        self,
        *,
        original_url: str,
        short_code: str,
        expires_at: datetime | None = None,
        owner_id: UUID | None = None,
        title: str | None = None,
    ) -> URL:
        url = URL(
            original_url=original_url,
            short_code=short_code,
            expires_at=expires_at,
            owner_id=owner_id,
            title=title,
        )
        self._session.add(url)
        await self._session.flush()
        await self._session.refresh(url)
        return url

    async def increment_click_count(self, short_code: str) -> None:
        await self._session.execute(
            update(URL)
            .where(URL.short_code == short_code)
            .values(click_count=URL.click_count + 1)
        )

    async def delete_by_short_code(self, short_code: str) -> bool:
        result = await self._session.execute(
            delete(URL).where(URL.short_code == short_code)
        )
        return result.rowcount > 0

    async def deactivate(self, short_code: str) -> bool:
        result = await self._session.execute(
            update(URL)
            .where(URL.short_code == short_code)
            .values(is_active=False)
        )
        return result.rowcount > 0

    async def list_by_owner(
        self,
        owner_id: UUID,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> list[URL]:
        """Return all URLs belonging to a user, newest first."""
        result = await self._session.execute(
            select(URL)
            .where(URL.owner_id == owner_id)
            .order_by(URL.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
