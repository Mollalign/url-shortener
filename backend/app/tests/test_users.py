"""
Test suite for user management endpoints.

Run with:
    uv run pytest app/tests/ -v
"""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.deps import get_current_user, get_db, get_redis
from app.db.base import Base
from app.main import app

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

# ---------------------------------------------------------------------------
# Fixtures (shared with test_urls.py pattern)
# ---------------------------------------------------------------------------

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
    redis.delete = AsyncMock(side_effect=lambda *keys: [store.pop(k, None) for k in keys])
    redis.incr = AsyncMock(return_value=1)
    redis.expire = AsyncMock(return_value=True)
    redis.ping = AsyncMock(return_value=True)
    return redis


@pytest_asyncio.fixture()
async def client(db_session: AsyncSession, mock_redis):
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
# Helpers
# ---------------------------------------------------------------------------

_REGISTER_PAYLOAD = {
    "email": "test@example.com",
    "username": "testuser",
    "password": "Secure123",
}


async def _register_and_get_token(client: AsyncClient) -> str:
    """Register a user and return the JWT token."""
    resp = await client.post("/api/v1/auth/register", json=_REGISTER_PAYLOAD)
    assert resp.status_code == 201, resp.text
    return resp.json()["access_token"]


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

class TestRegister:
    async def test_register_returns_201_with_token(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/register", json=_REGISTER_PAYLOAD)
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["username"] == "testuser"
        # password must never appear in response
        assert "password" not in data["user"]
        assert "hashed_password" not in data["user"]

    async def test_duplicate_email_returns_409(self, client: AsyncClient):
        await client.post("/api/v1/auth/register", json=_REGISTER_PAYLOAD)
        resp = await client.post(
            "/api/v1/auth/register",
            json={**_REGISTER_PAYLOAD, "username": "other"},
        )
        assert resp.status_code == 409

    async def test_duplicate_username_returns_409(self, client: AsyncClient):
        await client.post("/api/v1/auth/register", json=_REGISTER_PAYLOAD)
        resp = await client.post(
            "/api/v1/auth/register",
            json={**_REGISTER_PAYLOAD, "email": "other@example.com"},
        )
        assert resp.status_code == 409

    async def test_weak_password_returns_422(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/auth/register",
            json={**_REGISTER_PAYLOAD, "password": "nouppercaseordigit"},
        )
        assert resp.status_code == 422

    async def test_invalid_email_returns_422(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/auth/register",
            json={**_REGISTER_PAYLOAD, "email": "not-an-email"},
        )
        assert resp.status_code == 422

    async def test_invalid_username_chars_returns_422(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/auth/register",
            json={**_REGISTER_PAYLOAD, "username": "bad user!"},
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

class TestLogin:
    async def test_login_returns_token(self, client: AsyncClient):
        await _register_and_get_token(client)
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "Secure123"},
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    async def test_wrong_password_returns_400(self, client: AsyncClient):
        await _register_and_get_token(client)
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "WrongPass99"},
        )
        assert resp.status_code == 400

    async def test_unknown_email_returns_400(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@example.com", "password": "Secure123"},
        )
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Profile — GET /users/me
# ---------------------------------------------------------------------------

class TestGetMe:
    async def test_get_me_returns_profile(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"

    async def test_get_me_no_token_returns_401(self, client: AsyncClient):
        resp = await client.get("/api/v1/users/me")
        assert resp.status_code == 401

    async def test_get_me_bad_token_returns_401(self, client: AsyncClient):
        resp = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer not.a.real.token"},
        )
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Profile — PATCH /users/me
# ---------------------------------------------------------------------------

class TestUpdateMe:
    async def test_update_username(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.patch(
            "/api/v1/users/me",
            json={"username": "newname"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["username"] == "newname"

    async def test_update_password_allows_new_login(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        await client.patch(
            "/api/v1/users/me",
            json={"password": "NewPass999"},
            headers={"Authorization": f"Bearer {token}"},
        )
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "NewPass999"},
        )
        assert resp.status_code == 200

    async def test_update_to_taken_username_returns_409(self, client: AsyncClient):
        # Register second user
        await client.post(
            "/api/v1/auth/register",
            json={"email": "second@example.com", "username": "seconduser", "password": "Secure123"},
        )
        token = await _register_and_get_token(client)
        resp = await client.patch(
            "/api/v1/users/me",
            json={"username": "seconduser"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 409


# ---------------------------------------------------------------------------
# My URLs — GET /users/me/urls
# ---------------------------------------------------------------------------

class TestMyURLs:
    async def test_list_my_urls_empty(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.get(
            "/api/v1/users/me/urls",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_authenticated_url_appears_in_my_urls(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        # Create URL while authenticated
        await client.post(
            "/api/v1/urls",
            json={"long_url": "https://example.com"},
            headers={"Authorization": f"Bearer {token}"},
        )
        resp = await client.get(
            "/api/v1/users/me/urls",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["long_url"] == "https://example.com"

    async def test_anonymous_url_not_in_my_urls(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        # Create URL without token (anonymous)
        await client.post("/api/v1/urls", json={"long_url": "https://example.com"})
        resp = await client.get(
            "/api/v1/users/me/urls",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_list_my_urls_requires_auth(self, client: AsyncClient):
        resp = await client.get("/api/v1/users/me/urls")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Delete account — DELETE /users/me
# ---------------------------------------------------------------------------

class TestDeleteMe:
    async def test_delete_me_deactivates_account(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.delete(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 204

    async def test_deleted_account_cannot_login(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        await client.delete(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "Secure123"},
        )
        assert resp.status_code == 400

    async def test_delete_me_requires_auth(self, client: AsyncClient):
        resp = await client.delete("/api/v1/users/me")
        assert resp.status_code == 401
