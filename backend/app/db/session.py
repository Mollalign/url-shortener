"""
Database engine and session management.

Responsibilities:
- Initialize the SQLAlchemy async engine
- Create the session factory
- Dispose the engine on shutdown
- Provide context-managed sessions for background tasks

FastAPI dependencies belong in `app.api.deps`.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def init_engine() -> AsyncEngine:
    """
    Initialize the global SQLAlchemy engine.

    This function should be called once during FastAPI startup.
    """
    global _engine, _sessionmaker

    if _engine is not None:
        return _engine

    settings = get_settings()

    _engine = create_async_engine(
        settings.database_url,
        echo=settings.db_echo,
        pool_pre_ping=True,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=settings.db_pool_timeout,
        pool_recycle=1800,
    )

    _sessionmaker = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    logger.info(
        "Database engine initialized"
    )

    return _engine


async def dispose_engine() -> None:
    """
    Dispose the SQLAlchemy engine and close all pooled connections.
    """
    global _engine, _sessionmaker

    if _engine is not None:
        await _engine.dispose()
        logger.info("Database engine disposed.")

    _engine = None
    _sessionmaker = None


def get_engine() -> AsyncEngine:
    """
    Return the initialized SQLAlchemy engine.
    """
    if _engine is None:
        raise RuntimeError(
            "Database engine has not been initialized. "
            "Call init_engine() during application startup."
        )

    return _engine


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """
    Return the configured async session factory.
    """
    if _sessionmaker is None:
        raise RuntimeError(
            "Session factory has not been initialized. "
            "Call init_engine() during application startup."
        )

    return _sessionmaker


@asynccontextmanager
async def session_scope() -> AsyncGenerator[AsyncSession, None]:
    """
    Context-managed database session.

    Intended for:
    - Background workers
    - Scheduled jobs
    - CLI scripts
    - Startup tasks

    Automatically commits on success and rolls back on failure.
    """

    session_factory = get_sessionmaker()

    async with session_factory() as session:
        try:
            yield session
            await session.commit()

        except Exception:
            await session.rollback()
            raise

        finally:
            await session.close()