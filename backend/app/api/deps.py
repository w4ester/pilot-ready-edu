"""Shared dependencies for API endpoints."""

from __future__ import annotations

from fastapi import Header, HTTPException, Request, status

from ..core.settings import get_settings


def get_current_user(
    request: Request,
    dev_user_id_header: str | None = Header(None, alias="X-Dev-User-Id"),
) -> str:
    """Resolve the authenticated user id from the session or dev overrides."""

    session_user = request.session.get("user_id")
    if session_user:
        return session_user

    settings = get_settings()
    fallback_user = dev_user_id_header or settings.dev_user_id
    if fallback_user:
        return fallback_user

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthenticated")
