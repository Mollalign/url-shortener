"""
Test suite for URL shortener endpoints.

Run with:
    PYTHONPATH=. uv run pytest app/tests/ -v
"""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.deps import get_db, get_redis
from app.db.base import Base
from app.main import app

# ---------------------------------------------------------------------------
# In-memory SQLite engine for tests (no Postgres needed)
# ---------------------------------------------------------------------------

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture()
async def db_session():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture()
async def mock_redis():
    store: dict = {}

    redis = AsyncMock()
    redis.get = AsyncMock(side_effect=lambda k: store.get(k))
    redis.set = AsyncMock(side_effect=lambda k, v, **kw: store.update({k: v}))
    redis.delete = AsyncMock(
        side_effect=lambda *keys: [store.pop(k, None) for k in keys]
    )
    redis.incr = AsyncMock(return_value=1)
    redis.expire = AsyncMock(return_value=True)
    redis.ping = AsyncMock(return_value=True)
    return redis


@pytest_asyncio.fixture()
async def client(db_session: AsyncSession, mock_redis):
    # Override DB and Redis dependencies
    async def _override_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_redis] = lambda: mock_redis

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCreateURL:
    async def test_create_returns_201(self, client: AsyncClient):
        resp = await client.post("/api/v1/urls", json={"long_url": "https://example.com"})
        assert resp.status_code == 201
        data = resp.json()
        assert "short_url" in data
        assert "alias" in data
        assert data["expires_at"] is None

    async def test_create_with_custom_alias(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/urls",
            json={"long_url": "https://example.com", "custom_alias": "my-link"},
        )
        assert resp.status_code == 201
        assert resp.json()["alias"] == "my-link"

    async def test_duplicate_custom_alias_returns_409(self, client: AsyncClient):
        body = {"long_url": "https://example.com", "custom_alias": "dupe-alias"}
        await client.post("/api/v1/urls", json=body)
        resp = await client.post("/api/v1/urls", json=body)
        assert resp.status_code == 409

    async def test_invalid_scheme_returns_422(self, client: AsyncClient):
        resp = await client.post("/api/v1/urls", json={"long_url": "ftp://example.com"})
        assert resp.status_code == 422

    async def test_invalid_alias_characters_returns_422(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/urls",
            json={"long_url": "https://example.com", "custom_alias": "bad alias!"},
        )
        assert resp.status_code == 422


class TestRedirect:
    async def test_redirect_returns_302(self, client: AsyncClient):
        create_resp = await client.post(
            "/api/v1/urls", json={"long_url": "https://example.com"}
        )
        assert create_resp.status_code == 201
        alias = create_resp.json()["alias"]

        resp = await client.get(f"/{alias}", follow_redirects=False)
        assert resp.status_code == 302
        assert resp.headers["location"] == "https://example.com"

    async def test_unknown_short_code_returns_404(self, client: AsyncClient):
        resp = await client.get("/nonexistent123", follow_redirects=False)
        assert resp.status_code == 404


class TestURLMetadata:
    async def test_get_metadata_returns_200(self, client: AsyncClient):
        create_resp = await client.post(
            "/api/v1/urls", json={"long_url": "https://example.com"}
        )
        alias = create_resp.json()["alias"]

        resp = await client.get(f"/api/v1/urls/{alias}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["long_url"] == "https://example.com"
        assert "clicks" in data

    async def test_unknown_code_metadata_returns_404(self, client: AsyncClient):
        resp = await client.get("/api/v1/urls/doesnotexist")
        assert resp.status_code == 404


class TestDeleteURL:
    async def test_delete_returns_204(self, client: AsyncClient):
        create_resp = await client.post(
            "/api/v1/urls", json={"long_url": "https://example.com"}
        )
        alias = create_resp.json()["alias"]

        resp = await client.delete(f"/api/v1/urls/{alias}")
        assert resp.status_code == 204

    async def test_delete_unknown_returns_404(self, client: AsyncClient):
        resp = await client.delete("/api/v1/urls/doesnotexist")
        assert resp.status_code == 404

    async def test_deleted_url_redirects_404(self, client: AsyncClient):
        create_resp = await client.post(
            "/api/v1/urls", json={"long_url": "https://example.com"}
        )
        alias = create_resp.json()["alias"]
        await client.delete(f"/api/v1/urls/{alias}")

        resp = await client.get(f"/{alias}", follow_redirects=False)
        assert resp.status_code == 404


class TestHealth:
    async def test_liveness(self, client: AsyncClient):
        resp = await client.get("/api/v1/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
