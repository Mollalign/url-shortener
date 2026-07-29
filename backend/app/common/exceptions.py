"""
Domain exceptions mapped to HTTP status codes.
"""

from __future__ import annotations

from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    def __init__(self, message: str = "Resource not found.") -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=message)


class GoneException(HTTPException):
    def __init__(self, message: str = "Resource no longer available.") -> None:
        super().__init__(status_code=status.HTTP_410_GONE, detail=message)


class ConflictException(HTTPException):
    def __init__(self, message: str = "Resource already exists.") -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=message)


class BadRequestException(HTTPException):
    def __init__(self, message: str = "Bad request.") -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


class RateLimitException(HTTPException):
    def __init__(self, message: str = "Rate limit exceeded. Try again later.") -> None:
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=message,
            headers={"Retry-After": "60"},
        )
