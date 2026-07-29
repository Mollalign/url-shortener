"""
Top-level API v1 router — pure aggregator.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.url.router import router as url_router
from app.api.v1.users.router import router as users_router

api_router = APIRouter()

# Infrastructure
api_router.include_router(health_router)

# Resources
api_router.include_router(url_router)
api_router.include_router(users_router)