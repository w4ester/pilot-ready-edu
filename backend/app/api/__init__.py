# backend/app/api/__init__.py
"""Aggregate API routers for the Edinfinite backend."""

from fastapi import APIRouter, Depends

from ..core.csrf import require_csrf
from . import auth, health, libraries, models, ollama_proxy, prompts, rooms, tools

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router)
api_router.include_router(tools.router, dependencies=[Depends(require_csrf)])
api_router.include_router(models.router, dependencies=[Depends(require_csrf)])
api_router.include_router(prompts.router, dependencies=[Depends(require_csrf)])
api_router.include_router(libraries.router, dependencies=[Depends(require_csrf)])
api_router.include_router(rooms.router, dependencies=[Depends(require_csrf)])
api_router.include_router(ollama_proxy.router)
