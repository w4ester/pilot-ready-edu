"""Prompt management endpoints: list/create/update/test."""

from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..db.models import CreatedPrompt
from ..db.session import get_db
from .deps import get_current_user


router = APIRouter(prefix="/api/v1/prompts", tags=["prompts"])


class PromptIn(BaseModel):
    command: str = Field(..., min_length=2)
    title: Optional[str] = None
    content: str
    variables: Dict[str, Any] | None = None
    access_control: Dict[str, Any] | None = None


class PromptOut(BaseModel):
    id: str
    command: str
    title: Optional[str] = None
    updated_at: int | None = None


@router.get("", response_model=list[PromptOut])
def list_prompts(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> list[PromptOut]:
    items = (
        db.query(CreatedPrompt)
        .filter(CreatedPrompt.user_id == user_id)
        .order_by(CreatedPrompt.updated_at.desc())
        .all()
    )
    return [
        PromptOut(id=p.id, command=p.command, title=p.title, updated_at=p.updated_at)
        for p in items
    ]


@router.post("", response_model=PromptOut, status_code=status.HTTP_201_CREATED)
def create_prompt(
    payload: PromptIn,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> PromptOut:
    if not payload.command.startswith("/"):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "command_must_start_with_slash")

    exists = (
        db.query(CreatedPrompt)
        .filter(CreatedPrompt.user_id == user_id)
        .filter(func.lower(CreatedPrompt.command) == payload.command.lower())
        .first()
    )
    if exists:
        raise HTTPException(status.HTTP_409_CONFLICT, "prompt_command_exists")

    prompt = CreatedPrompt(
        id=str(uuid.uuid4()),
        user_id=user_id,
        command=payload.command,
        title=payload.title,
        content=payload.content,
        variables=payload.variables or {},
        access_control=payload.access_control or {},
    )
    db.add(prompt)
    db.commit()

    return PromptOut(id=prompt.id, command=prompt.command, title=prompt.title, updated_at=prompt.updated_at)


class PromptUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    variables: Dict[str, Any] | None = None
    access_control: Dict[str, Any] | None = None


@router.put("/{prompt_id}", response_model=PromptOut)
def update_prompt(
    prompt_id: str,
    payload: PromptUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> PromptOut:
    prompt = (
        db.query(CreatedPrompt)
        .filter(CreatedPrompt.id == prompt_id, CreatedPrompt.user_id == user_id)
        .first()
    )
    if not prompt:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "prompt_not_found")

    if payload.title is not None:
        prompt.title = payload.title
    if payload.content is not None:
        prompt.content = payload.content
    if payload.variables is not None:
        prompt.variables = payload.variables
    if payload.access_control is not None:
        prompt.access_control = payload.access_control
    db.add(prompt)
    db.commit()

    return PromptOut(id=prompt.id, command=prompt.command, title=prompt.title, updated_at=prompt.updated_at)


class PromptTestIn(BaseModel):
    content: str
    variables: Dict[str, Any] | None = None


@router.post("/test")
def test_prompt(payload: PromptTestIn) -> Dict[str, Any]:
    # Naive formatter: Python format_map with provided variables
    variables = payload.variables or {}
    try:
        rendered = payload.content.format_map({k: variables.get(k, "") for k in variables.keys()})
        return {"ok": True, "rendered": rendered}
    except KeyError as e:
        return {"ok": False, "error": f"missing_variable: {e}"}
    except Exception as e:  # pragma: no cover - safety catch
        return {"ok": False, "error": str(e)}
