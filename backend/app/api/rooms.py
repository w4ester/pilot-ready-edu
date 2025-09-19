"""Rooms & Messaging endpoints with assistant and knowledge stubs."""

from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db.models import (
    ClassAssistant,
    ClassKnowledge,
    ClassMessage,
    ClassRoom,
    ClassRoomMember,
    Library,
)
from ..db.session import get_db
from .deps import get_current_user


router = APIRouter(prefix="/api/v1", tags=["rooms"])


def _require_room_access(db: Session, room_id: str, user_id: str) -> ClassRoom:
    room = db.query(ClassRoom).filter(ClassRoom.id == room_id).first()
    if not room:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "room_not_found")

    if room.created_by_user_id == user_id:
        return room

    membership = (
        db.query(ClassRoomMember)
        .filter(
            ClassRoomMember.class_room_id == room_id,
            ClassRoomMember.user_id == user_id,
        )
        .first()
    )
    if not membership:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "room_access_denied")

    return room


class MessageIn(BaseModel):
    content: str
    parent_id: Optional[str] = None
    target_user_id: Optional[str] = None
    data: Dict[str, Any] | None = None
    meta: Dict[str, Any] | None = None


class MessageOut(BaseModel):
    id: str
    user_id: str
    class_room_id: str
    content: str
    created_at: int | None = None
    parent_id: Optional[str] = None


@router.get("/rooms/{room_id}/messages", response_model=list[MessageOut])
def list_messages(
    room_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> list[MessageOut]:
    _require_room_access(db, room_id, user_id)

    msgs = (
        db.query(ClassMessage)
        .filter(ClassMessage.class_room_id == room_id)
        .order_by(ClassMessage.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        MessageOut(
            id=m.id,
            user_id=m.user_id,
            class_room_id=m.class_room_id,
            content=m.content,
            created_at=m.created_at,
            parent_id=m.parent_id,
        )
        for m in msgs
    ]


@router.post("/rooms/{room_id}/messages", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
def post_message(
    room_id: str,
    payload: MessageIn,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> MessageOut:
    _require_room_access(db, room_id, user_id)

    msg = ClassMessage(
        id=str(uuid.uuid4()),
        user_id=user_id,
        class_room_id=room_id,
        parent_id=payload.parent_id,
        target_user_id=payload.target_user_id,
        content=payload.content,
        data=payload.data or {},
        meta=payload.meta or {},
    )
    db.add(msg)
    db.commit()

    return MessageOut(
        id=msg.id,
        user_id=msg.user_id,
        class_room_id=msg.class_room_id,
        content=msg.content,
        created_at=msg.created_at,
        parent_id=msg.parent_id,
    )


class AssistantIn(BaseModel):
    model_id: str
    name: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    invocation_mode: str = "manual"
    tool_config: Dict[str, Any] | None = None


class AssistantOut(BaseModel):
    id: str
    class_room_id: str
    model_id: str
    name: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: float
    invocation_mode: str
    is_active: bool


@router.get("/class_rooms/{room_id}/assistant", response_model=AssistantOut)
def get_assistant(
    room_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> AssistantOut:
    _require_room_access(db, room_id, user_id)

    asst = (
        db.query(ClassAssistant)
        .filter(ClassAssistant.class_room_id == room_id)
        .order_by(ClassAssistant.created_at.asc())
        .first()
    )
    if not asst:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "assistant_not_found")
    return AssistantOut(
        id=asst.id,
        class_room_id=asst.class_room_id,
        model_id=asst.model_id,
        name=asst.name,
        system_prompt=asst.system_prompt,
        temperature=float(asst.temperature or 0.7),
        invocation_mode=asst.invocation_mode,
        is_active=asst.is_active,
    )


@router.post("/class_rooms/{room_id}/assistant")
def upsert_assistant(
    room_id: str,
    payload: AssistantIn,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_room_access(db, room_id, user_id)

    # Upsert assistant for room
    asst = (
        db.query(ClassAssistant)
        .filter(ClassAssistant.class_room_id == room_id)
        .order_by(ClassAssistant.created_at.asc())
        .first()
    )
    if asst is None:
        asst = ClassAssistant(
            id=str(uuid.uuid4()),
            class_room_id=room_id,
            created_by_user_id=user_id,
            model_id=payload.model_id,
            name=payload.name,
            system_prompt=payload.system_prompt,
            temperature=payload.temperature,
            invocation_mode=payload.invocation_mode,
            tool_config=payload.tool_config or {},
        )
    else:
        asst.model_id = payload.model_id
        asst.name = payload.name
        asst.system_prompt = payload.system_prompt
        asst.temperature = payload.temperature
        asst.invocation_mode = payload.invocation_mode
        asst.tool_config = payload.tool_config or {}

    db.add(asst)
    db.commit()

    # Stubbed reply (placeholder)
    return {
        "assistant_id": asst.id,
        "message": "Assistant configured. Stubbed reply: Hello from the assistant!",
    }


class KnowledgeIn(BaseModel):
    library_ids: list[str]


@router.post("/class_rooms/{room_id}/knowledge")
def attach_knowledge(
    room_id: str,
    payload: KnowledgeIn,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_room_access(db, room_id, user_id)

    owned_libraries = {
        lib.id
        for lib in (
            db.query(Library)
            .filter(Library.user_id == user_id)
            .filter(Library.id.in_(payload.library_ids))
            .all()
        )
    }
    missing = [lid for lid in payload.library_ids if lid not in owned_libraries]

    attached = 0
    for lid in payload.library_ids:
        if lid not in owned_libraries:
            continue
        db.merge(
            ClassKnowledge(
                class_room_id=room_id,
                library_id=lid,
                created_by_user_id=user_id,
            )
        )
        attached += 1
    db.commit()
    return {"attached": attached, "missing": missing}
