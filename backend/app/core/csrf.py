"""CSRF protection utilities."""

from __future__ import annotations

import hmac

from fastapi import HTTPException, Request, status

from .settings import get_settings

_SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


def require_csrf(request: Request) -> None:
    """Validate CSRF token for state-changing requests using double-submit cookie."""

    if request.method.upper() in _SAFE_METHODS:
        return

    settings = get_settings()
    header_token = request.headers.get("X-CSRF-Token")
    cookie_token = request.cookies.get(settings.csrf_cookie_name)

    if not header_token or not cookie_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="csrf_validation_failed",
        )

    if not hmac.compare_digest(header_token, cookie_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="csrf_validation_failed",
        )
