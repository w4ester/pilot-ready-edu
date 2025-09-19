"""Authentication endpoints."""

from __future__ import annotations

from typing import Final

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from ..core.security import utc_now_ms, verify_password
from ..db.models import UserAuth
from ..db.session import get_db
from .deps import get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

_MAX_FAILED_ATTEMPTS: Final[int] = 5
_LOCKOUT_DURATION_MS: Final[int] = 15 * 60 * 1000  # 15 minutes


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    user_id: str
    email: EmailStr
    requires_password_change: bool


class MeResponse(BaseModel):
    user_id: str
    email: EmailStr | None
    auth_method: str
    requires_password_change: bool


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> LoginResponse:
    """Authenticate a user with email/password and start a session."""

    normalized_email = payload.email.strip()
    user = (
        db.query(UserAuth)
        .filter(UserAuth.email == normalized_email)
        .one_or_none()
    )

    # Always return the same error for unknown users.
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_credentials",
        )

    now_ms = utc_now_ms()

    if user.locked_until and user.locked_until > now_ms:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="account_locked",
        )

    if not verify_password(payload.password, user.password):
        failed_attempts = (user.failed_attempts or 0) + 1
        user.failed_attempts = failed_attempts
        if failed_attempts >= _MAX_FAILED_ATTEMPTS:
            user.locked_until = now_ms + _LOCKOUT_DURATION_MS
            user.failed_attempts = 0
        user.updated_at = now_ms
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_credentials",
        )

    # Successful login: reset counters and establish session.
    user.failed_attempts = 0
    user.locked_until = None
    user.last_login_at = now_ms
    user.updated_at = now_ms
    db.commit()

    request.session.clear()
    request.session["user_id"] = user.id
    request.session["auth_method"] = user.auth_method or "password"

    return LoginResponse(
        user_id=user.id,
        email=user.email,
        requires_password_change=bool(user.requires_password_change),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request) -> Response:
    """Clear the current session."""

    request.session.clear()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=MeResponse)
def read_current_user(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MeResponse:
    """Return the current authenticated user profile."""

    user = db.query(UserAuth).filter(UserAuth.id == user_id).one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="unauthenticated",
        )

    return MeResponse(
        user_id=user.id,
        email=user.email,
        auth_method=user.auth_method,
        requires_password_change=bool(user.requires_password_change),
    )
