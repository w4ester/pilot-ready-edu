# backend/app/api/__init__.py
"""Aggregate API routers for the Edinfinite backend."""

from fastapi import APIRouter

from . import auth, health, libraries, models, prompts, rooms, tools

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router)
api_router.include_router(tools.router)
api_router.include_router(models.router)
api_router.include_router(prompts.router)
api_router.include_router(libraries.router)
api_router.include_router(rooms.router)
