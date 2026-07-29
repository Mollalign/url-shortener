"""
User and authentication endpoints.

POST /auth/register  — create account, receive JWT
POST /auth/login     — authenticate, receive JWT
GET  /users/me       — current user profile (requires auth)
PATCH /users/me      — update username or password (requires auth)
GET  /users/me/urls  — list current user's short URLs (requires auth)
DELETE /users/me     — deactivate account (requires auth)
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.repositories.url import URLRepository
from app.schemas.url import URLMetaResponse
from app.schemas.user import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
    UserUpdateRequest,
)
from app.services.user import UserService

router = APIRouter(tags=["users"])


def _svc(session: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(session)


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

@router.post(
    "/auth/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    body: UserRegisterRequest,
    svc: UserService = Depends(_svc),
) -> TokenResponse:
    return await svc.register(
        email=body.email,
        username=body.username,
        password=body.password,
    )


@router.post(
    "/auth/login",
    response_model=TokenResponse,
    summary="Login and receive a JWT access token",
)
async def login(
    body: UserLoginRequest,
    svc: UserService = Depends(_svc),
) -> TokenResponse:
    return await svc.login(email=body.email, password=body.password)


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

@router.get(
    "/users/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.patch(
    "/users/me",
    response_model=UserResponse,
    summary="Update username or password",
)
async def update_me(
    body: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    svc: UserService = Depends(_svc),
) -> UserResponse:
    updated = await svc.update_profile(
        current_user.id,
        username=body.username,
        password=body.password,
    )
    return UserResponse.model_validate(updated)


@router.get(
    "/users/me/urls",
    response_model=list[URLMetaResponse],
    summary="List all short URLs created by the current user",
)
async def list_my_urls(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[URLMetaResponse]:
    from app.core.config import get_settings
    settings = get_settings()

    repo = URLRepository(session)
    urls = await repo.list_by_owner(current_user.id, skip=skip, limit=limit)

    base = settings.base_url.rstrip("/")
    return [
        URLMetaResponse(
            short_url=f"{base}/{u.short_code}",
            long_url=u.original_url,
            created_at=u.created_at,
            expires_at=u.expires_at,
            clicks=u.click_count,
        )
        for u in urls
    ]


@router.delete(
    "/users/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate current user account",
)
async def delete_me(
    current_user: User = Depends(get_current_user),
    svc: UserService = Depends(_svc),
) -> None:
    await svc.delete_account(current_user.id)
