"""
User service — business logic for registration, authentication, and profile management.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BadRequestException, ConflictException, NotFoundException
from app.core.logging import get_logger
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import TokenResponse, UserResponse

log = get_logger(__name__)


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = UserRepository(session)
        self._session = session

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def register(
        self,
        *,
        email: str,
        username: str,
        password: str,
    ) -> TokenResponse:
        """Create a new user account and return a JWT token."""
        if await self._repo.email_exists(email):
            raise ConflictException(f"Email '{email}' is already registered.")

        if await self._repo.username_exists(username):
            raise ConflictException(f"Username '{username}' is already taken.")

        user = await self._repo.create(
            email=email,
            username=username,
            hashed_password=hash_password(password),
        )
        await self._session.commit()

        log.info("user.registered", user_id=str(user.id), username=username)

        token = create_access_token(user.id)
        return TokenResponse(
            access_token=token,
            user=UserResponse.model_validate(user),
        )

    async def login(self, *, email: str, password: str) -> TokenResponse:
        """Authenticate a user and return a JWT token."""
        user = await self._repo.get_by_email(email)

        if user is None or not verify_password(password, user.hashed_password):
            # Deliberately vague to prevent email enumeration
            raise BadRequestException("Invalid email or password.")

        if not user.is_active:
            raise BadRequestException("This account has been deactivated.")

        log.info("user.logged_in", user_id=str(user.id))

        token = create_access_token(user.id)
        return TokenResponse(
            access_token=token,
            user=UserResponse.model_validate(user),
        )

    async def get_profile(self, user_id: UUID) -> User:
        """Return the User ORM object by ID."""
        user = await self._repo.get_by_id(user_id)
        if user is None:
            raise NotFoundException("User not found.")
        return user

    async def update_profile(
        self,
        user_id: UUID,
        *,
        username: str | None,
        password: str | None,
    ) -> User:
        """Update username and/or password for the given user."""
        user = await self._repo.get_by_id(user_id)
        if user is None:
            raise NotFoundException("User not found.")

        if username and username != user.username:
            if await self._repo.username_exists(username):
                raise ConflictException(f"Username '{username}' is already taken.")
            await self._repo.update_username(user, username)

        if password:
            await self._repo.update_password(user, hash_password(password))

        await self._session.commit()
        await self._session.refresh(user)

        log.info("user.updated", user_id=str(user.id))
        return user

    async def delete_account(self, user_id: UUID) -> None:
        """Soft-delete by deactivating the account."""
        user = await self._repo.get_by_id(user_id)
        if user is None:
            raise NotFoundException("User not found.")

        await self._repo.deactivate(user)
        await self._session.commit()
        log.info("user.deactivated", user_id=str(user_id))
