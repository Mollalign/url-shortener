"""
Standard response envelopes.
"""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """`{ "data": ... }` envelope for single-resource responses."""

    model_config = ConfigDict(from_attributes=True)

    data: T
    meta: dict[str, object] = Field(default_factory=dict)


class ListResponse(BaseModel, Generic[T]):
    """List envelope with optional pagination metadata."""

    model_config = ConfigDict(from_attributes=True)

    data: list[T]
    meta: dict[str, object] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    status: str = "ok"
    environment: str
    version: str
    db: bool
    redis: bool


def ok(data: T, meta: dict[str, object] | None = None) -> SuccessResponse[T]:
    return SuccessResponse[T](data=data, meta=meta or {})
