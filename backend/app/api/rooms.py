"""Rooms & Messaging endpoints with assistant and knowledge stubs."""

from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..core.security import utc_now_ms
from ..db.models import (
    ClassAssistant,
    ClassKnowledge,
    ClassMessage,
    ClassRoom,
    ClassRoomMember,
    Library,
    UserGroup,
    UserGroupMember,
)
from ..db.session import get_db
from .deps import get_current_user


router = APIRouter(prefix="/api/v1", tags=["rooms"])


class RoomSummary(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    member_count: int
    is_archived: bool
    created_at: int | None = None
    channel_type: Optional[str] = None
    data: Dict[str, Any]
    meta: Dict[str, Any]


def _summarize_room(room: ClassRoom, member_count: int) -> RoomSummary:
    return RoomSummary(
        id=room.id,
        name=room.name,
        description=room.description,
        member_count=member_count,
        is_archived=room.is_archived,
        created_at=room.created_at,
        channel_type=room.channel_type,
        data=room.data or {},
        meta=room.meta or {},
    )


class RoomCreate(BaseModel):
    name: str
    description: Optional[str] = None
    channel_type: Optional[str] = None
    data: Dict[str, Any] | None = None
    meta: Dict[str, Any] | None = None
    access_control: Dict[str, Any] | None = None


class RoomCreate(BaseModel):
    name: str
    description: Optional[str] = None
    channel_type: Optional[str] = None
    data: Dict[str, Any] | None = None
    meta: Dict[str, Any] | None = None
    access_control: Dict[str, Any] | None = None
    member_ids: list[str] | None = None


class RoomUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    channel_type: Optional[str] = None
    data: Dict[str, Any] | None = None
    meta: Dict[str, Any] | None = None
    access_control: Dict[str, Any] | None = None


def _room_summary(db: Session, room: ClassRoom) -> RoomSummary:
    member_count = (
        db.query(func.count(ClassRoomMember.user_id))
        .filter(ClassRoomMember.class_room_id == room.id)
        .scalar()
    )
    return RoomSummary(
        id=room.id,
        name=room.name,
        description=room.description,
        member_count=int(member_count or 0),
        is_archived=room.is_archived,
        created_at=room.created_at,
    )


@router.get("/rooms", response_model=list[RoomSummary])
def list_rooms(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> list[RoomSummary]:
    rooms = (
        db.query(ClassRoom)
        .filter(ClassRoom.created_by_user_id == user_id)
        .order_by(ClassRoom.created_at.desc())
        .all()
    )
    if not rooms:
        return []

    room_ids = [room.id for room in rooms]
    counts = dict(
        db.query(ClassRoomMember.class_room_id, func.count(ClassRoomMember.user_id))
        .filter(ClassRoomMember.class_room_id.in_(room_ids))
        .group_by(ClassRoomMember.class_room_id)
        .all()
    )


@router.post("/rooms", response_model=RoomSummary, status_code=status.HTTP_201_CREATED)
def create_room(
    payload: RoomCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> RoomSummary:
    group_id = str(uuid.uuid4())
    group = UserGroup(id=group_id)
    db.add(group)
    db.flush()

    db.merge(
        UserGroupMember(
            group_id=group_id,
            user_id=user_id,
            role_in_group="owner",
        )
    )

    room_id = str(uuid.uuid4())
    room = ClassRoom(
        id=room_id,
        class_id=group_id,
        created_by_user_id=user_id,
        name=payload.name,
        description=payload.description,
        channel_type=payload.channel_type,
        data=payload.data or {},
        meta=payload.meta or {},
        access_control=payload.access_control or {},
    )
    db.add(room)
    db.add(ClassRoomMember(class_room_id=room_id, user_id=user_id))
    db.commit()
    db.refresh(room)

    return _summarize_room(room, member_count=1)


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
