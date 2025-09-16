"""Model management endpoints for Creation Station."""

from __future__ import annotations

import os
import uuid
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db.models import CreatedModel, CreatedTool, Library, ModelLibrary, ModelTool
from ..db.session import get_db


router = APIRouter(prefix="/api/v1/models", tags=["models"])


def get_current_user(
    dev_user_id: Optional[str] = Header(None, alias="X-Dev-User-Id")
) -> str:
    user_id = dev_user_id or os.getenv("DEV_USER_ID")
    if not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing_user_id")
    return user_id


class ModelIn(BaseModel):
    name: str
    base_model_id: str = "gpt-oss:20B"
    params: Dict[str, Any] | None = None
    meta: Dict[str, Any] | None = None
    access_control: Dict[str, Any] | None = None


class ModelOut(BaseModel):
    id: str
    name: str
    base_model_id: str
    is_active: bool
    updated_at: int | None = None


@router.get("", response_model=list[ModelOut])
def list_models(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> list[ModelOut]:
    records = (
        db.query(CreatedModel)
        .filter(CreatedModel.user_id == user_id)
        .order_by(CreatedModel.updated_at.desc())
        .all()
    )
    return [
        ModelOut(
            id=model.id,
            name=model.name,
            base_model_id=model.base_model_id,
            is_active=model.is_active,
            updated_at=model.updated_at,
        )
        for model in records
    ]


@router.post("", response_model=ModelOut, status_code=status.HTTP_201_CREATED)
def create_model(
    payload: ModelIn,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> ModelOut:
    model = CreatedModel(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name=payload.name,
        base_model_id=payload.base_model_id,
        params=payload.params or {},
        meta=payload.meta or {},
        access_control=payload.access_control or {},
    )
    db.add(model)
    db.commit()

    return ModelOut(
        id=model.id,
        name=model.name,
        base_model_id=model.base_model_id,
        is_active=model.is_active,
        updated_at=model.updated_at,
    )


class AttachPayload(BaseModel):
    tool_ids: list[str] | None = None
    library_ids: list[str] | None = None
    order_index: Optional[int] = None


@router.post("/{model_id}/tools")
def attach_tools(
    model_id: str,
    payload: AttachPayload,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> dict[str, Any]:
    if not payload.tool_ids:
        return {"attached": 0}

    model = (
        db.query(CreatedModel)
        .filter(CreatedModel.id == model_id, CreatedModel.user_id == user_id)
        .first()
    )
    if not model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "model_not_found")

    existing_tools = {
        t.id for t in db.query(CreatedTool).filter(CreatedTool.id.in_(payload.tool_ids)).all()
    }
    missing = [tid for tid in payload.tool_ids if tid not in existing_tools]

    for idx, tool_id in enumerate(payload.tool_ids, start=1):
        db.merge(
            ModelTool(
                model_id=model_id,
                tool_id=tool_id,
                order_index=payload.order_index or idx,
            )
        )
    db.commit()

    return {
        "attached": len(payload.tool_ids),
        "missing": missing,
    }


@router.post("/{model_id}/libraries")
def attach_libraries(
    model_id: str,
    payload: AttachPayload,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> dict[str, Any]:
    if not payload.library_ids:
        return {"attached": 0}

    model = (
        db.query(CreatedModel)
        .filter(CreatedModel.id == model_id, CreatedModel.user_id == user_id)
        .first()
    )
    if not model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "model_not_found")

    existing = {
        lib.id for lib in db.query(Library).filter(Library.id.in_(payload.library_ids)).all()
    }
    missing = [lid for lid in payload.library_ids if lid not in existing]

    for idx, library_id in enumerate(payload.library_ids, start=1):
        db.merge(
            ModelLibrary(
                model_id=model_id,
                library_id=library_id,
                order_index=payload.order_index or idx,
            )
        )
    db.commit()

    return {
        "attached": len(payload.library_ids),
        "missing": missing,
    }


@router.post("/{model_id}/export/ollama")
def export_ollama(
    model_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> dict[str, str]:
    model = (
        db.query(CreatedModel)
        .filter(CreatedModel.id == model_id, CreatedModel.user_id == user_id)
        .first()
    )
    if not model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "model_not_found")

    text = """FROM {base_model}\nPARAMS {params}\n""".format(
        base_model=model.base_model_id,
        params=model.params or {},
    )
    return {"modelfile": text}
