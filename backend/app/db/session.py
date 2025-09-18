# backend/app/db/session.py
"""Database session management utilities."""

from __future__ import annotations

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.settings import get_settings


_settings = get_settings()

engine = create_engine(
    _settings.database_url,
    future=True,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session for request scope."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
