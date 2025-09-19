"""Authentication and security helper utilities."""

from __future__ import annotations

from datetime import datetime, timezone

from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Return a bcrypt hash for the provided password."""

    return _pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str | None) -> bool:
    """Validate a plain password against a stored hash."""

    if not hashed_password:
        return False
    return _pwd_context.verify(plain_password, hashed_password)


def utc_now_ms() -> int:
    """Current UTC timestamp in milliseconds."""

    return int(datetime.now(tz=timezone.utc).timestamp() * 1000)
