"""SQLAlchemy models mirroring the canonical Edinfinite schema."""

from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from .base import Base


def _json_default() -> dict:
    return {}


_NOW_MS = text("now_ms()")


class CreatedTool(Base):
    __tablename__ = "created_tool"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("user_profile.id", ondelete="CASCADE"), nullable=False)
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
    specs = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
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

    id = Column(String, primary_key=True)
    tool_id = Column(String, ForeignKey("created_tool.id", ondelete="CASCADE"), nullable=False, index=True)
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

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("user_profile.id", ondelete="CASCADE"), nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    data = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    meta = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    access_control = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)


class CreatedModel(Base):
    __tablename__ = "created_model"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("user_profile.id", ondelete="CASCADE"), nullable=False)
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

    model_id = Column(String, ForeignKey("created_model.id", ondelete="CASCADE"), primary_key=True)
    tool_id = Column(String, ForeignKey("created_tool.id", ondelete="CASCADE"), primary_key=True)
    order_index = Column(Integer, nullable=True)
    config = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    enabled = Column(Boolean, nullable=False, server_default=text("true"))
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)


class ModelLibrary(Base):
    __tablename__ = "model_library"

    model_id = Column(String, ForeignKey("created_model.id", ondelete="CASCADE"), primary_key=True)
    library_id = Column(String, ForeignKey("library.id", ondelete="CASCADE"), primary_key=True)
    order_index = Column(Integer, nullable=True)
    retrieval = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
