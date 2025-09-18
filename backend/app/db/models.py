"""SQLAlchemy models mirroring the canonical Edinfinite schema."""

from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    Computed,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import CITEXT, JSONB, TSVECTOR, UUID
from pgvector.sqlalchemy import Vector
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


class LibraryDocument(Base):
    __tablename__ = "library_document"

    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    library_id = Column(
        UUID(as_uuid=False),
        ForeignKey("library.id", ondelete="CASCADE"),
        nullable=False,
    )
    source = Column(Text, nullable=True)
    uri = Column(Text, nullable=True)
    title = Column(Text, nullable=True)
    meta = Column(JSONB, nullable=True, server_default=text("'{}'::jsonb"))
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)

    __table_args__ = (
        Index("idx_library_document_library", "library_id"),
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunk"

    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    document_id = Column(
        UUID(as_uuid=False),
        ForeignKey("library_document.id", ondelete="CASCADE"),
        nullable=False,
    )
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(768), nullable=False)
    token_count = Column(Integer, nullable=True)
    meta = Column(JSONB, nullable=True)
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    content_tsv = Column(
        TSVECTOR,
        Computed("to_tsvector('english', coalesce(content, ''))", persisted=True),
    )

    __table_args__ = (
        CheckConstraint(
            "chunk_index >= 0", name="ck_document_chunk_index_nonnegative"
        ),
        Index("idx_document_chunk_doc", "document_id"),
        Index(
            "idx_document_chunk_unique",
            "document_id",
            "chunk_index",
            unique=True,
        ),
        Index(
            "idx_document_chunk_embedding_hnsw",
            text("embedding vector_cosine_ops"),
            postgresql_using="hnsw",
        ),
        Index(
            "idx_document_chunk_tsv_gin",
            "content_tsv",
            postgresql_using="gin",
        ),
    )


class LibraryFile(Base):
    __tablename__ = "library_file"

    library_id = Column(
        UUID(as_uuid=False),
        ForeignKey("library.id", ondelete="CASCADE"),
        primary_key=True,
    )
    file_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_file.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)

    __table_args__ = (
        Index("idx_library_file_file", "file_id"),
    )


class UserChat(Base):
    __tablename__ = "user_chat"

    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    owner_user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_profile.id", ondelete="CASCADE"),
        nullable=True,
    )
    channel_type = Column(Text, nullable=False, server_default=text("'direct'"))
    meta = Column(JSONB, nullable=True, server_default=text("'{}'::jsonb"))
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)

    __table_args__ = (
        Index("idx_user_chat_owner", "owner_user_id"),
    )


class UserChatTag(Base):
    __tablename__ = "user_chat_tag"

    chat_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_chat.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tag = Column(Text, primary_key=True)
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)


class UserTag(Base):
    __tablename__ = "user_tag"

    id = Column(String, primary_key=True)
    user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_profile.id", ondelete="CASCADE"),
        primary_key=True,
    )
    name = Column(Text, nullable=False)
    meta = Column(JSONB, nullable=True, server_default=text("'{}'::jsonb"))


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


class UserAuth(Base):
    __tablename__ = "user_auth"

    id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_profile.id", ondelete="CASCADE"),
        primary_key=True,
    )
    email = Column(CITEXT, nullable=False, unique=True)
    password = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    last_login_at = Column(BigInteger, nullable=True)
    failed_attempts = Column(Integer, nullable=False, server_default=text("0"))
    locked_until = Column(BigInteger, nullable=True)
    auth_method = Column(Text, nullable=False, server_default=text("'password'"))
    requires_password_change = Column(
        Boolean, nullable=False, server_default=text("false")
    )


class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_profile.id", ondelete="CASCADE"),
        primary_key=True,
    )
    default_model = Column(
        String(100), nullable=False, server_default=text("'gpt-oss:20B'")
    )
    default_temperature = Column(Numeric, nullable=False, server_default=text("0.7"))
    default_max_tokens = Column(Integer, nullable=False, server_default=text("500"))
    embedding_model = Column(
        String(100), nullable=False, server_default=text("'embeddinggemma:300m'")
    )
    auto_save = Column(Boolean, nullable=False, server_default=text("true"))
    auto_save_interval = Column(Integer, nullable=False, server_default=text("30"))
    theme = Column(String(20), nullable=False, server_default=text("'light'"))
    preferences = Column(JSONB, nullable=True, server_default=text("'{}'::jsonb"))
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)


class UserIdentity(Base):
    __tablename__ = "user_identity"

    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_profile.id", ondelete="CASCADE"),
        nullable=False,
    )
    provider = Column(Text, nullable=False)
    subject = Column(Text, nullable=False)
    email = Column(CITEXT, nullable=True)
    email_verified = Column(Boolean, nullable=False, server_default=text("false"))
    raw_profile = Column(JSONB, nullable=True)
    is_primary = Column(Boolean, nullable=False, server_default=text("false"))
    connected_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    last_login_at = Column(BigInteger, nullable=True)
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)

    __table_args__ = (
        UniqueConstraint("provider", "subject", name="uq_user_identity_provider_subject"),
    )


class UserFile(Base):
    __tablename__ = "user_file"

    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_profile.id", ondelete="CASCADE"),
        nullable=False,
    )
    hash = Column(Text, nullable=True)
    filename = Column(Text, nullable=False)
    path = Column(Text, nullable=True)
    data = Column(JSONB, nullable=True, server_default=text("'{}'::jsonb"))
    meta = Column(JSONB, nullable=True, server_default=text("'{}'::jsonb"))
    access_control = Column(JSONB, nullable=True, server_default=text("'{}'::jsonb"))
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)

    __table_args__ = (
        Index("idx_user_file_user", "user_id"),
    )


class UserFolder(Base):
    __tablename__ = "user_folder"

    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    parent_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_folder.id", ondelete="CASCADE"),
        nullable=True,
    )
    user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_profile.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(Text, nullable=False)
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)

    __table_args__ = (
        Index("idx_user_folder_user", "user_id"),
        Index("idx_user_folder_parent", "parent_id"),
    )


class Organization(Base):
    __tablename__ = "organization"

    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name = Column(Text, nullable=False)
    slug = Column(Text, nullable=True, unique=True)
    meta = Column(JSONB, nullable=True, server_default=text("'{}'::jsonb"))
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)


class OrganizationDomain(Base):
    __tablename__ = "organization_domain"

    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    organization_id = Column(
        UUID(as_uuid=False),
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False,
    )
    domain = Column(Text, nullable=False)
    verified = Column(Boolean, nullable=False, server_default=text("false"))
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)


Index(
    "ux_org_domain_lower",
    func.lower(OrganizationDomain.domain),
    unique=True,
)


class OrganizationIdp(Base):
    __tablename__ = "organization_idp"

    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    organization_id = Column(
        UUID(as_uuid=False),
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False,
    )
    provider = Column(Text, nullable=False)
    config = Column(JSONB, nullable=False)
    is_enabled = Column(Boolean, nullable=False, server_default=text("true"))
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)


Index(
    "ux_org_provider_lower",
    OrganizationIdp.organization_id,
    func.lower(OrganizationIdp.provider),
    unique=True,
)


class UserGroup(Base):
    __tablename__ = "user_group"

    id = Column(UUID(as_uuid=False), primary_key=True)


class UserGroupMember(Base):
    __tablename__ = "user_group_member"

    group_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_group.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_profile.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role_in_group = Column(Text, nullable=False)
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
