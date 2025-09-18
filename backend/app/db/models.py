"""SQLAlchemy models mirroring the canonical Edinfinite schema."""

from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from .base import Base


def _json_default() -> dict:
    return {}


_NOW_MS = text("now_ms()")


class CreatedTool(Base):
    __tablename__ = "created_tool"

    id = Column(UUID(as_uuid=False), primary_key=True)
    user_id = Column(UUID(as_uuid=False), ForeignKey("user_profile.id", ondelete="CASCADE"), nullable=False)
    slug = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    language = Column(Text, nullable=False, server_default=text("'python'"))
    entrypoint = Column(Text, nullable=False, server_default=text("'run'"))
    content = Column(Text, nullable=False)
    requirements = Column(Text, nullable=True)
    sandbox_profile = Column(Text, nullable=False, server_default=text("'restricted'"))
    timeout_ms = Column(Integer, nullable=False, server_default=text("60000"))
    memory_limit_mb = Column(Integer, nullable=False, server_default=text("512"))
    meta = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    valves = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    access_control = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)

    versions = relationship(
        "CreatedToolVersion",
        back_populates="tool",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("user_id", "slug", name="ux_created_tool_owner_slug"),
    )


class CreatedToolVersion(Base):
    __tablename__ = "created_tool_version"

    id = Column(UUID(as_uuid=False), primary_key=True)
    tool_id = Column(UUID(as_uuid=False), ForeignKey("created_tool.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    requirements = Column(Text, nullable=True)
    meta = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)

    tool = relationship("CreatedTool", back_populates="versions")

    __table_args__ = (
        UniqueConstraint("tool_id", "version", name="uq_created_tool_version"),
    )


class Library(Base):
    __tablename__ = "library"

    id = Column(UUID(as_uuid=False), primary_key=True)
    user_id = Column(UUID(as_uuid=False), ForeignKey("user_profile.id", ondelete="CASCADE"), nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    data = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    meta = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    access_control = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)


class CreatedModel(Base):
    __tablename__ = "created_model"

    id = Column(UUID(as_uuid=False), primary_key=True)
    user_id = Column(UUID(as_uuid=False), ForeignKey("user_profile.id", ondelete="CASCADE"), nullable=False)
    base_model_id = Column(Text, nullable=False, server_default=text("'gpt-oss:20B'"))
    name = Column(Text, nullable=False)
    params = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    meta = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    access_control = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)

    tools = relationship("ModelTool", cascade="all, delete-orphan", lazy="selectin")
    libraries = relationship("ModelLibrary", cascade="all, delete-orphan", lazy="selectin")


class ModelTool(Base):
    __tablename__ = "model_tool"

    model_id = Column(UUID(as_uuid=False), ForeignKey("created_model.id", ondelete="CASCADE"), primary_key=True)
    tool_id = Column(UUID(as_uuid=False), ForeignKey("created_tool.id", ondelete="CASCADE"), primary_key=True)
    order_index = Column(Integer, nullable=True)
    config = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    enabled = Column(Boolean, nullable=False, server_default=text("true"))


class ModelLibrary(Base):
    __tablename__ = "model_library"

    model_id = Column(UUID(as_uuid=False), ForeignKey("created_model.id", ondelete="CASCADE"), primary_key=True)
    library_id = Column(UUID(as_uuid=False), ForeignKey("library.id", ondelete="CASCADE"), primary_key=True)
    order_index = Column(Integer, nullable=True)
    retrieval = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))


# ===================== Prompts =====================


class CreatedPrompt(Base):
    __tablename__ = "created_prompt"

    id = Column(UUID(as_uuid=False), primary_key=True)
    command = Column(String(64), nullable=False)
    user_id = Column(UUID(as_uuid=False), ForeignKey("user_profile.id", ondelete="CASCADE"), nullable=False)
    title = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    variables = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    access_control = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)

    __table_args__ = (
        UniqueConstraint("user_id", "command", name="ux_created_prompt_user_cmd"),
    )


# ===================== Rooms & Messaging =====================


class ClassRoom(Base):
    __tablename__ = "class_room"

    id = Column(UUID(as_uuid=False), primary_key=True)
    class_id = Column(UUID(as_uuid=False), ForeignKey("user_group.id", ondelete="CASCADE"), nullable=False)
    created_by_user_id = Column(UUID(as_uuid=False), ForeignKey("user_profile.id", ondelete="CASCADE"), nullable=False)
    name = Column(Text, nullable=False)
    channel_type = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    data = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    meta = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    access_control = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    is_archived = Column(Boolean, nullable=False, server_default=text("false"))
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)


class ClassRoomMember(Base):
    __tablename__ = "class_room_member"

    class_room_id = Column(UUID(as_uuid=False), ForeignKey("class_room.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(UUID(as_uuid=False), ForeignKey("user_profile.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)


class ClassReadReceipt(Base):
    __tablename__ = "class_read_receipt"

    class_room_id = Column(UUID(as_uuid=False), ForeignKey("class_room.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(UUID(as_uuid=False), ForeignKey("user_profile.id", ondelete="CASCADE"), primary_key=True)
    last_read_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)


class ClassMessage(Base):
    __tablename__ = "class_message"

    id = Column(UUID(as_uuid=False), primary_key=True)
    user_id = Column(UUID(as_uuid=False), ForeignKey("user_profile.id", ondelete="CASCADE"), nullable=False)
    class_room_id = Column(UUID(as_uuid=False), ForeignKey("class_room.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(UUID(as_uuid=False), ForeignKey("class_message.id", ondelete="CASCADE"), nullable=True)
    target_user_id = Column(UUID(as_uuid=False), ForeignKey("user_profile.id", ondelete="CASCADE"), nullable=True)
    content = Column(Text, nullable=False)
    data = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    meta = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)


class ClassMessageReaction(Base):
    __tablename__ = "class_message_reaction"

    id = Column(UUID(as_uuid=False), primary_key=True)
    user_id = Column(UUID(as_uuid=False), ForeignKey("user_profile.id", ondelete="CASCADE"), nullable=False)
    message_id = Column(UUID(as_uuid=False), ForeignKey("class_message.id", ondelete="CASCADE"), nullable=False)
    name = Column(Text, nullable=False)
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)


class ClassAssistant(Base):
    __tablename__ = "class_assistant"

    id = Column(UUID(as_uuid=False), primary_key=True)
    class_room_id = Column(UUID(as_uuid=False), ForeignKey("class_room.id", ondelete="CASCADE"), nullable=False)
    created_by_user_id = Column(UUID(as_uuid=False), ForeignKey("user_profile.id"), nullable=False)
    model_id = Column(Text, nullable=False)
    name = Column(Text, nullable=True)
    system_prompt = Column(Text, nullable=True)
    temperature = Column(Numeric, nullable=False, server_default=text("0.7"))
    invocation_mode = Column(Text, nullable=False, server_default=text("'manual'"))
    tool_config = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)


class ClassKnowledge(Base):
    __tablename__ = "class_knowledge"

    class_room_id = Column(UUID(as_uuid=False), ForeignKey("class_room.id", ondelete="CASCADE"), primary_key=True)
    library_id = Column(UUID(as_uuid=False), ForeignKey("library.id", ondelete="CASCADE"), primary_key=True)
    created_by_user_id = Column(UUID(as_uuid=False), ForeignKey("user_profile.id"), nullable=False)
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
class UserProfile(Base):
    __tablename__ = "user_profile"

    id = Column(UUID(as_uuid=False), primary_key=True)


class UserGroup(Base):
    __tablename__ = "user_group"

    id = Column(UUID(as_uuid=False), primary_key=True)
