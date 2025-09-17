"""Library endpoints: list/add for user libraries."""

from __future__ import annotations

import os
import uuid
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db.models import Library
from ..db.session import get_db


router = APIRouter(prefix="/api/v1/libraries", tags=["libraries"])


def get_current_user(
    dev_user_id: Optional[str] = Header(None, alias="X-Dev-User-Id")
) -> str:
    user_id = dev_user_id or os.getenv("DEV_USER_ID")
    if not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing_user_id")
    return user_id


class LibraryIn(BaseModel):
    name: str
    description: Optional[str] = None
    data: Dict[str, Any] | None = None
    meta: Dict[str, Any] | None = None
    access_control: Dict[str, Any] | None = None


class LibraryOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    updated_at: int | None = None


@router.get("", response_model=list[LibraryOut])
def list_libraries(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> list[LibraryOut]:
    items = (
        db.query(Library)
        .filter(Library.user_id == user_id)
        .order_by(Library.updated_at.desc())
        .all()
    )
    return [
        LibraryOut(id=lib.id, name=lib.name, description=lib.description, updated_at=lib.updated_at)
        for lib in items
    ]


@router.post("", response_model=LibraryOut, status_code=status.HTTP_201_CREATED)
def create_library(
    payload: LibraryIn,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> LibraryOut:
    lib = Library(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name=payload.name,
        description=payload.description,
        data=payload.data or {},
        meta=payload.meta or {},
        access_control=payload.access_control or {},
    )
    db.add(lib)
    db.commit()
    return LibraryOut(id=lib.id, name=lib.name, description=lib.description, updated_at=lib.updated_at)

