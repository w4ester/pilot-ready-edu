from __future__ import annotations

"""Tool management endpoints for Creation Station."""

import uuid
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..db.models import CreatedTool, CreatedToolVersion
from ..db.session import get_db
from .deps import get_current_user


router = APIRouter(prefix="/api/v1/tools", tags=["tools"])


class ToolBase(BaseModel):
    slug: str = Field(..., pattern=r"^[a-zA-Z0-9_-]+$")
    name: str
    language: str = "python"
    entrypoint: str = "run"
    content: str
    requirements: Optional[str] = None
    valves: Dict[str, Any] | None = None
    meta: Dict[str, Any] | None = None
    access_control: Dict[str, Any] | None = None
    sandbox_profile: str = "restricted"
    timeout_ms: int = 60000
    memory_limit_mb: int = 512


class ToolOut(BaseModel):
    id: str
    slug: str
    name: str
    language: str
    entrypoint: str
    is_active: bool
    updated_at: int | None = None
    content: str


class ToolDeleteOut(BaseModel):
    slug: str
    status: str = "deleted"


@router.get("", response_model=list[ToolOut])
def list_tools(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> list[ToolOut]:
    items = (
        db.query(CreatedTool)
        .filter(CreatedTool.user_id == user_id)
        .order_by(CreatedTool.updated_at.desc())
        .all()
    )
    return [
        ToolOut(
            id=tool.id,
            slug=tool.slug,
            name=tool.name,
            language=tool.language,
            entrypoint=tool.entrypoint,
            is_active=tool.is_active,
            updated_at=tool.updated_at,
            content=tool.content,
        )
        for tool in items
    ]


@router.post("", response_model=ToolOut, status_code=status.HTTP_201_CREATED)
def create_tool(
    payload: ToolBase,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> ToolOut:
    slug = payload.slug.lower()

    existing = (
        db.query(CreatedTool)
        .filter(CreatedTool.user_id == user_id)
        .filter(func.lower(CreatedTool.slug) == slug)
        .first()
    )
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "tool_slug_exists")

    tool_id = str(uuid.uuid4())
    tool = CreatedTool(
        id=tool_id,
        user_id=user_id,
        slug=slug,
        name=payload.name,
        language=payload.language,
        entrypoint=payload.entrypoint,
        content=payload.content,
        requirements=payload.requirements,
        valves=payload.valves or {},
        meta=payload.meta or {},
        access_control=payload.access_control or {},
        sandbox_profile=payload.sandbox_profile,
        timeout_ms=payload.timeout_ms,
        memory_limit_mb=payload.memory_limit_mb,
    )
    db.add(tool)

    version = CreatedToolVersion(
        id=str(uuid.uuid4()),
        tool_id=tool_id,
        version=1,
        content=payload.content,
        requirements=payload.requirements,
        meta=payload.meta or {},
    )
    db.add(version)
    db.commit()

    return ToolOut(
        id=tool.id,
        slug=tool.slug,
        name=tool.name,
        language=tool.language,
        entrypoint=tool.entrypoint,
        is_active=tool.is_active,
        updated_at=tool.updated_at,
        content=tool.content,
    )


class PublishIn(BaseModel):
    content: str
    requirements: Optional[str] = None
    meta: Dict[str, Any] | None = None


@router.post("/{tool_id}/versions", status_code=status.HTTP_201_CREATED)
def publish_version(
    tool_id: str,
    payload: PublishIn,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> dict[str, Any]:
    tool = (
        db.query(CreatedTool)
        .filter(CreatedTool.id == tool_id, CreatedTool.user_id == user_id)
        .first()
    )
    if not tool:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "tool_not_found")

    latest = (
        db.query(func.max(CreatedToolVersion.version))
        .filter(CreatedToolVersion.tool_id == tool_id)
        .scalar()
    )
    next_version = (latest or 0) + 1

    version = CreatedToolVersion(
        id=str(uuid.uuid4()),
        tool_id=tool_id,
        version=next_version,
        content=payload.content,
        requirements=payload.requirements,
        meta=payload.meta or {},
    )
    tool.content = payload.content
    tool.requirements = payload.requirements
    db.add(version)
    db.add(tool)
    db.commit()

    return {"tool_id": tool_id, "version": next_version}


class TestRunIn(BaseModel):
    code: str
    input: Dict[str, Any] | None = None


@router.delete("/{slug}", response_model=ToolDeleteOut)
def delete_tool(
    slug: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> ToolDeleteOut:
    slug_lower = slug.lower()

    tool = (
        db.query(CreatedTool)
        .filter(CreatedTool.user_id == user_id)
        .filter(func.lower(CreatedTool.slug) == slug_lower)
        .first()
    )
    if not tool:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "tool_not_found")

    db.delete(tool)
    db.commit()

    return ToolDeleteOut(slug=tool.slug)


@router.post("/test-run")
def test_run(payload: TestRunIn) -> dict[str, Any]:
    return {
        "ok": True,
        "message": f"Sandbox disabled. Received {len(payload.code or '')} characters.",
    }
