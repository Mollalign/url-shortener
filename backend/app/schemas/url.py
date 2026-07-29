"""
Pydantic schemas for URL operations.
"""

from __future__ import annotations

import re
from datetime import datetime
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# Requests
# ---------------------------------------------------------------------------

class URLCreateRequest(BaseModel):
    long_url: str = Field(..., description="The destination URL to shorten.")
    custom_alias: str | None = Field(
        default=None,
        description="Optional custom alias (alphanumeric, hyphens, underscores).",
    )
    expiration_date: datetime | None = Field(
        default=None,
        description="Optional expiry time in ISO 8601 UTC.",
    )

    @field_validator("long_url")
    @classmethod
    def validate_long_url(cls, v: str) -> str:
        parsed = urlparse(v)
        if parsed.scheme not in ("http", "https"):
            raise ValueError("Only http and https URLs are allowed.")
        if not parsed.netloc:
            raise ValueError("URL must have a valid domain.")
        return v

    @field_validator("custom_alias")
    @classmethod
    def validate_custom_alias(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Custom alias may only contain letters, digits, hyphens, and underscores."
            )
        if not (3 <= len(v) <= 50):
            raise ValueError("Custom alias must be between 3 and 50 characters.")
        return v

    @field_validator("expiration_date")
    @classmethod
    def validate_expiration_date(cls, v: datetime | None) -> datetime | None:
        if v is None:
            return v
        from datetime import timezone
        now = datetime.now(timezone.utc)
        if v.tzinfo is None:
            raise ValueError("expiration_date must be timezone-aware (UTC).")
        if v <= now:
            raise ValueError("expiration_date must be in the future.")
        return v


# ---------------------------------------------------------------------------
# Responses
# ---------------------------------------------------------------------------

class URLCreateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    short_url: str
    alias: str
    expires_at: datetime | None = None


class URLMetaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    short_url: str
    long_url: str
    created_at: datetime
    expires_at: datetime | None = None
    clicks: int


class ErrorResponse(BaseModel):
    error: str
    message: str
