"""Shared dependencies for API endpoints."""

from __future__ import annotations

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from ..core.settings import get_settings
from ..db.models import UserAuth
from ..db.session import get_db


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    dev_user_id_header: str | None = Header(None, alias="X-Dev-User-Id"),
) -> str:
    """Resolve the authenticated user id from the session or dev overrides."""

    settings = get_settings()

    session_user = request.session.get("user_id")
    session_nonce = request.session.get("nv")
    if session_user and session_nonce:
        user = db.query(UserAuth).filter(UserAuth.id == session_user).one_or_none()
        if user and user.session_nonce == session_nonce:
            return session_user
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthenticated")

    if settings.allow_dev_override:
        fallback_user = dev_user_id_header or settings.dev_user_id
        if fallback_user:
            return fallback_user

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthenticated")
