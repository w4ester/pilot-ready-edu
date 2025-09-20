from __future__ import annotations

"""Tool management endpoints for Creation Station."""

import uuid
from typing import Any, Dict, Literal, Optional

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
    requirements: Optional[str] = None


class AssistantMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(..., min_length=1)


class AssistantIn(BaseModel):
    messages: list[AssistantMessage] = Field(..., min_items=1)


class AssistantOut(BaseModel):
    messages: list[AssistantMessage]
    suggestions: list[str]


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
            requirements=tool.requirements,
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
        requirements=tool.requirements,
    )


class PublishIn(BaseModel):
    content: str
    requirements: Optional[str] = None
    meta: Dict[str, Any] | None = None


def _build_suggestions(messages: list[AssistantMessage]) -> tuple[str, list[str]]:
    """Return a conversational reply and structured suggestions."""

    last_user_message = ""
    for message in reversed(messages):
        if message.role == "user" and message.content.strip():
            last_user_message = message.content.strip()
            break

    normalized = last_user_message.lower()

    suggestions: list[str] = []
    if "test" in normalized or "unit" in normalized:
        suggestions.append(
            "Write targeted unit tests with pytest to pin down the expected behaviour before refactoring."
        )
    if "optimiz" in normalized or "performance" in normalized or "slow" in normalized:
        suggestions.append(
            "Profile the slow sections and consider vectorising loops or caching repeated computations."
        )
    if any(keyword in normalized for keyword in ["error", "bug", "exception", "fail"]):
        suggestions.append(
            "Add defensive input validation and wrap risky calls in try/except blocks to surface clearer errors."
        )
    if "document" in normalized or "explain" in normalized or "docstring" in normalized:
        suggestions.append(
            "Document the tool's expected inputs, outputs, and edge cases with a concise docstring."
        )

    if not suggestions:
        suggestions.extend(
            [
                "Sketch the tool's responsibilities, required inputs, and edge cases before coding.",
                "Add descriptive logging or print statements while iterating so you can verify behaviour quickly.",
                "Consider writing a small usage example that demonstrates the happy path once the function is ready.",
            ]
        )

    if last_user_message:
        intro = "Here's how you can move forward based on what you just shared:\n\n"
    else:
        intro = "Here are a few ideas to get started with your tool:\n\n"

    reply = intro + "\n".join(f"• {item}" for item in suggestions)
    return reply, suggestions


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


@router.post("/assistant", response_model=AssistantOut)
def tool_assistant(
    payload: AssistantIn,
    user_id: str = Depends(get_current_user),
) -> AssistantOut:
    del user_id  # Authenticated user required by dependency; not used in stub implementation.

    reply, suggestions = _build_suggestions(payload.messages)
    message = AssistantMessage(role="assistant", content=reply)
    return AssistantOut(messages=[message], suggestions=suggestions)


@router.post("/test-run")
def test_run(payload: TestRunIn) -> dict[str, Any]:
    return {
        "ok": True,
        "message": f"Sandbox disabled. Received {len(payload.code or '')} characters.",
    }
