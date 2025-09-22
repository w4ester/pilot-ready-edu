"""SQLAlchemy models mirroring the canonical Edinfinite schema."""

from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    Computed,
    Float,
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
from sqlalchemy.dialects.postgresql import CITEXT, ENUM, JSONB, TSVECTOR, UUID
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import relationship

from .base import Base


def _json_default() -> dict:
    return {}


_NOW_MS = text("now_ms()")


class CreatedTool(Base):
    __tablename__ = "created_tool"

    id = Column(UUID(as_uuid=False), primary_key=True)
    user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_profile.id", ondelete="CASCADE"),
        nullable=False,
    )
    slug = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    language = Column(Text, nullable=False, server_default=text("'python'"))
    entrypoint = Column(Text, nullable=True)
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
    tool_id = Column(
        UUID(as_uuid=False),
        ForeignKey("created_tool.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
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
    user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_profile.id", ondelete="CASCADE"),
        nullable=False,
    )
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

    __table_args__ = (Index("idx_library_document_library", "library_id"),)


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
        CheckConstraint("chunk_index >= 0", name="ck_document_chunk_index_nonnegative"),
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

    __table_args__ = (Index("idx_library_file_file", "file_id"),)


class UserChat(Base):
    __tablename__ = "user_chat"

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
    title = Column(Text, nullable=True)
    conversation = Column(JSONB, nullable=False)
    share_id = Column(Text, nullable=True, unique=True)
    archived = Column(Boolean, nullable=False, server_default=text("false"))
    pinned = Column(Boolean, nullable=False, server_default=text("false"))
    meta = Column(JSONB, nullable=True, server_default=text("'{}'::jsonb"))
    folder_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_folder.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)

    __table_args__ = (
        Index("idx_user_chat_user", "user_id"),
        Index("idx_user_chat_folder", "folder_id"),
    )


class UserChatTag(Base):
    __tablename__ = "user_chat_tag"

    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tag_name = Column(Text, nullable=False)
    chat_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_chat.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_profile.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)

    __table_args__ = (
        Index(
            "ux_user_chat_tag_user_chat_name",
            user_id,
            chat_id,
            func.lower(tag_name),
            unique=True,
        ),
    )


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


# ===================== Artifacts & Sharing =====================


class UserArtifact(Base):
    __tablename__ = "user_artifact"

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
    chat_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_chat.id", ondelete="SET NULL"),
        nullable=True,
    )
    group_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_group.id", ondelete="SET NULL"),
        nullable=True,
    )
    title = Column(Text, nullable=False)
    type = Column(Text, nullable=False)
    language = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    subject_area = Column(Text, nullable=True)
    grade_level = Column(Text, nullable=True)
    version = Column(Integer, nullable=False, server_default=text("1"))
    parent_artifact_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_artifact.id", ondelete="SET NULL"),
        nullable=True,
    )
    meta = Column(JSONB, nullable=True, server_default=text("'{}'::jsonb"))
    access_control = Column(JSONB, nullable=True, server_default=text("'{}'::jsonb"))
    is_published = Column(Boolean, nullable=False, server_default=text("false"))
    is_template = Column(Boolean, nullable=False, server_default=text("false"))
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)

    __table_args__ = (
        CheckConstraint("version >= 1", name="ck_user_artifact_version_positive"),
        Index("idx_user_artifact_user", "user_id"),
        Index(
            "ux_user_artifact_lineage_version",
            func.coalesce(parent_artifact_id, id),
            version,
            unique=True,
        ),
    )


ResourceKindEnum = ENUM(name="resource_kind", create_type=False)


class ResourceShare(Base):
    __tablename__ = "resource_shares"

    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    resource_type = Column(ResourceKindEnum, nullable=False)
    resource_id = Column(UUID(as_uuid=False), nullable=False)
    grantee_group_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_group.id", ondelete="CASCADE"),
        nullable=True,
    )
    grantee_user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_profile.id", ondelete="CASCADE"),
        nullable=True,
    )
    permission = Column(Text, nullable=False)
    created_by = Column(
        UUID(as_uuid=False),
        ForeignKey("user_profile.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    expires_at = Column(BigInteger, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "permission IN ('view','use','edit','admin')",
            name="ck_resource_shares_permission",
        ),
        CheckConstraint(
            "(grantee_group_id IS NULL) <> (grantee_user_id IS NULL)",
            name="ck_resource_shares_single_grantee",
        ),
        Index(
            "ux_resource_share_target_grantee",
            resource_type,
            resource_id,
            grantee_group_id,
            grantee_user_id,
            unique=True,
        ),
    )


# ===================== Feedback, Memory, App Config =====================


class UserFeedback(Base):
    __tablename__ = "user_feedback"

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
    version = Column(BigInteger, nullable=False, server_default=text("0"))
    type = Column(Text, nullable=False)
    data = Column(JSONB, nullable=True)
    meta = Column(JSONB, nullable=True)
    snapshot = Column(JSONB, nullable=True)
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)


class UserMemory(Base):
    __tablename__ = "user_memory"

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
    content = Column(Text, nullable=False)
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)


class AppConfig(Base):
    __tablename__ = "app_config"

    id = Column(Integer, primary_key=True)
    data = Column(JSONB, nullable=False)
    version = Column(Integer, nullable=False)
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)


# ===================== BYOM Registry =====================


class ModelProvider(Base):
    __tablename__ = "model_provider"

    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name = Column(Text, nullable=False, unique=True)
    kind = Column(Text, nullable=False)
    config = Column(JSONB, nullable=True, server_default=text("'{}'::jsonb"))
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)


class BaseModel(Base):
    __tablename__ = "base_model"

    id = Column(Text, primary_key=True)
    provider_id = Column(
        UUID(as_uuid=False),
        ForeignKey("model_provider.id", ondelete="CASCADE"),
        nullable=False,
    )
    modality = Column(Text, nullable=False)
    embedding_dim = Column(Integer, nullable=True)
    meta = Column(JSONB, nullable=True, server_default=text("'{}'::jsonb"))
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)

    __table_args__ = (Index("idx_base_model_provider", "provider_id"),)


class ProviderCredential(Base):
    __tablename__ = "provider_credential"

    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_profile.id", ondelete="CASCADE"),
        nullable=True,
    )
    organization_id = Column(
        UUID(as_uuid=False),
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=True,
    )
    provider_id = Column(
        UUID(as_uuid=False),
        ForeignKey("model_provider.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(Text, nullable=False)
    secret_ref = Column(Text, nullable=False)
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)

    __table_args__ = (
        Index("idx_provider_credential_provider", "provider_id"),
        Index("idx_provider_credential_user", "user_id"),
        Index("idx_provider_credential_org", "organization_id"),
    )


# ===================== MCP (Model Context Protocol) =====================


class McpServer(Base):
    __tablename__ = "mcp_server"

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
    organization_id = Column(
        UUID(as_uuid=False),
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=True,
    )
    name = Column(Text, nullable=False)
    slug = Column(Text, nullable=True)
    transport = Column(Text, nullable=False)
    command = Column(Text, nullable=True)
    args = Column(JSONB, nullable=True)
    env = Column(JSONB, nullable=True)
    working_dir = Column(Text, nullable=True)
    sse_url = Column(Text, nullable=True)
    headers = Column(JSONB, nullable=True)
    auth_kind = Column(Text, nullable=False, server_default=text("'none'"))
    credential_id = Column(
        UUID(as_uuid=False),
        ForeignKey("provider_credential.id", ondelete="SET NULL"),
        nullable=True,
    )
    timeouts = Column(JSONB, nullable=True)
    is_enabled = Column(Boolean, nullable=False, server_default=text("true"))
    health_status = Column(Text, nullable=False, server_default=text("'unknown'"))
    last_seen_at = Column(BigInteger, nullable=True)
    last_error = Column(Text, nullable=True)
    provider_kind = Column(Text, nullable=False, server_default=text("'external'"))
    is_verified_provider = Column(Boolean, nullable=False, server_default=text("false"))
    certification = Column(JSONB, nullable=True)
    meta = Column(JSONB, nullable=True)
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)

    __table_args__ = (
        CheckConstraint(
            "transport IN ('stdio','sse')",
            name="ck_mcp_server_transport",
        ),
        CheckConstraint(
            "auth_kind IN ('none','bearer','basic','header')",
            name="ck_mcp_server_auth_kind",
        ),
        CheckConstraint(
            "health_status IN ('unknown','healthy','unreachable','error')",
            name="ck_mcp_server_health_status",
        ),
        CheckConstraint(
            "provider_kind IN ('internal','external')",
            name="ck_mcp_server_provider_kind",
        ),
        Index(
            "ux_mcp_server_owner_slug",
            owner_user_id,
            func.lower(func.coalesce(slug, name)),
            unique=True,
        ),
        Index("idx_mcp_server_org", "organization_id"),
    )


class McpServerTool(Base):
    __tablename__ = "mcp_server_tool"

    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    server_id = Column(
        UUID(as_uuid=False),
        ForeignKey("mcp_server.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    input_schema = Column(JSONB, nullable=False)
    is_enabled = Column(Boolean, nullable=False, server_default=text("true"))
    last_discovered_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)

    __table_args__ = (
        Index(
            "ux_mcp_server_tool_name",
            server_id,
            func.lower(name),
            unique=True,
        ),
        Index("idx_mcp_server_tool_server", "server_id"),
    )


class ModelMcpTool(Base):
    __tablename__ = "model_mcp_tool"

    model_id = Column(
        UUID(as_uuid=False),
        ForeignKey("created_model.id", ondelete="CASCADE"),
        primary_key=True,
    )
    server_id = Column(
        UUID(as_uuid=False),
        ForeignKey("mcp_server.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tool_name = Column(Text, primary_key=True)
    order_index = Column(Integer, nullable=True)
    config = Column(JSONB, nullable=True)
    enabled = Column(Boolean, nullable=False, server_default=text("true"))
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)

    __table_args__ = (Index("idx_model_mcp_tool_server", "server_id"),)


class McpServerVersion(Base):
    __tablename__ = "mcp_server_version"

    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    server_id = Column(
        UUID(as_uuid=False),
        ForeignKey("mcp_server.id", ondelete="CASCADE"),
        nullable=False,
    )
    version = Column(Integer, nullable=False)
    spec = Column(JSONB, nullable=False)
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)

    __table_args__ = (
        UniqueConstraint("server_id", "version", name="uq_mcp_server_version"),
    )


class McpServerBinding(Base):
    __tablename__ = "mcp_server_binding"

    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    server_id = Column(
        UUID(as_uuid=False),
        ForeignKey("mcp_server.id", ondelete="CASCADE"),
        nullable=False,
    )
    organization_id = Column(
        UUID(as_uuid=False),
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=True,
    )
    class_room_id = Column(
        UUID(as_uuid=False),
        ForeignKey("class_room.id", ondelete="CASCADE"),
        nullable=True,
    )
    model_id = Column(
        UUID(as_uuid=False),
        ForeignKey("created_model.id", ondelete="CASCADE"),
        nullable=True,
    )
    assistant_id = Column(
        UUID(as_uuid=False),
        ForeignKey("class_assistant.id", ondelete="CASCADE"),
        nullable=True,
    )
    enabled = Column(Boolean, nullable=False, server_default=text("true"))
    precedence = Column(Integer, nullable=False, server_default=text("0"))
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)

    __table_args__ = (
        CheckConstraint(
            "(((organization_id IS NOT NULL)::int + (class_room_id IS NOT NULL)::int + (model_id IS NOT NULL)::int + (assistant_id IS NOT NULL)::int) <= 1)",
            name="ck_mcp_server_binding_scope",
        ),
        Index(
            "ux_mcp_server_binding_scope",
            "server_id",
            "organization_id",
            "class_room_id",
            "model_id",
            "assistant_id",
            unique=True,
        ),
        Index("idx_mcp_server_binding_server", "server_id"),
        Index(
            "idx_mcp_server_binding_prec",
            server_id,
            precedence.desc(),
        ),
    )


# ===================== Platform Capabilities =====================


class PlatformCapability(Base):
    __tablename__ = "platform_capability"

    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    key = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    rollout_phase = Column(Text, nullable=False, server_default=text("'experimental'"))
    guardrails = Column(JSONB, nullable=True)
    meta = Column(JSONB, nullable=True)
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)

    __table_args__ = (
        CheckConstraint(
            "rollout_phase IN ('experimental','beta','ga','deprecated')",
            name="ck_platform_capability_rollout_phase",
        ),
        Index("ux_platform_capability_key", func.lower(key), unique=True),
    )


class PlatformCapabilityScope(Base):
    __tablename__ = "platform_capability_scope"

    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    capability_id = Column(
        UUID(as_uuid=False),
        ForeignKey("platform_capability.id", ondelete="CASCADE"),
        nullable=False,
    )
    organization_id = Column(
        UUID(as_uuid=False),
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=True,
    )
    class_room_id = Column(
        UUID(as_uuid=False),
        ForeignKey("class_room.id", ondelete="CASCADE"),
        nullable=True,
    )
    model_id = Column(
        UUID(as_uuid=False),
        ForeignKey("created_model.id", ondelete="CASCADE"),
        nullable=True,
    )
    assistant_id = Column(
        UUID(as_uuid=False),
        ForeignKey("class_assistant.id", ondelete="CASCADE"),
        nullable=True,
    )
    scope_label = Column(Text, nullable=True)
    enabled = Column(Boolean, nullable=False, server_default=text("true"))
    precedence = Column(Integer, nullable=False, server_default=text("0"))
    config = Column(JSONB, nullable=True)
    starts_at = Column(BigInteger, nullable=True)
    ends_at = Column(BigInteger, nullable=True)
    created_by = Column(
        UUID(as_uuid=False),
        ForeignKey("user_profile.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)

    __table_args__ = (
        CheckConstraint(
            "(((organization_id IS NOT NULL)::int + (class_room_id IS NOT NULL)::int + (model_id IS NOT NULL)::int + (assistant_id IS NOT NULL)::int) <= 1)",
            name="ck_platform_capability_scope_single_target",
        ),
        Index(
            "ux_platform_capability_scope",
            capability_id,
            organization_id,
            class_room_id,
            model_id,
            assistant_id,
            unique=True,
        ),
        Index("idx_platform_capability_scope_cap", capability_id),
        Index(
            "idx_platform_capability_scope_prec",
            capability_id,
            precedence.desc(),
        ),
        Index(
            "idx_platform_capability_scope_org",
            organization_id,
            postgresql_where=organization_id.isnot(None),
        ),
        Index(
            "idx_platform_capability_scope_room",
            class_room_id,
            postgresql_where=class_room_id.isnot(None),
        ),
        Index(
            "idx_platform_capability_scope_model",
            model_id,
            postgresql_where=model_id.isnot(None),
        ),
        Index(
            "idx_platform_capability_scope_assistant",
            assistant_id,
            postgresql_where=assistant_id.isnot(None),
        ),
    )


class ModelCapability(Base):
    __tablename__ = "model_capability"

    model_id = Column(
        UUID(as_uuid=False),
        ForeignKey("created_model.id", ondelete="CASCADE"),
        primary_key=True,
    )
    capability_id = Column(
        UUID(as_uuid=False),
        ForeignKey("platform_capability.id", ondelete="CASCADE"),
        primary_key=True,
    )
    enabled = Column(Boolean, nullable=False, server_default=text("true"))
    precedence = Column(Integer, nullable=False, server_default=text("0"))
    config = Column(JSONB, nullable=True)
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)

    __table_args__ = (Index("idx_model_capability_cap", capability_id),)


class PlatformFeatureFlag(Base):
    __tablename__ = "platform_feature_flag"

    key = Column(Text, primary_key=True)
    is_enabled = Column(Boolean, nullable=False, server_default=text("false"))
    effective_at = Column(BigInteger, nullable=True)
    sticky = Column(Boolean, nullable=False, server_default=text("false"))
    description = Column(Text, nullable=True)
    meta = Column(JSONB, nullable=True)
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)


class CreatedModel(Base):
    __tablename__ = "created_model"

    id = Column(UUID(as_uuid=False), primary_key=True)
    user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_profile.id", ondelete="CASCADE"),
        nullable=False,
    )
    base_model_id = Column(Text, nullable=True)
    name = Column(Text, nullable=False)
    params = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    meta = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    access_control = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)

    tools = relationship("ModelTool", cascade="all, delete-orphan", lazy="selectin")
    libraries = relationship(
        "ModelLibrary", cascade="all, delete-orphan", lazy="selectin"
    )


class ModelTool(Base):
    __tablename__ = "model_tool"

    model_id = Column(
        UUID(as_uuid=False),
        ForeignKey("created_model.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tool_id = Column(
        UUID(as_uuid=False),
        ForeignKey("created_tool.id", ondelete="CASCADE"),
        primary_key=True,
    )
    order_index = Column(Integer, nullable=True)
    config = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    enabled = Column(Boolean, nullable=False, server_default=text("true"))


class ModelLibrary(Base):
    __tablename__ = "model_library"

    model_id = Column(
        UUID(as_uuid=False),
        ForeignKey("created_model.id", ondelete="CASCADE"),
        primary_key=True,
    )
    library_id = Column(
        UUID(as_uuid=False),
        ForeignKey("library.id", ondelete="CASCADE"),
        primary_key=True,
    )
    order_index = Column(Integer, nullable=True)
    retrieval = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))


# ===================== Prompts =====================


class CreatedPrompt(Base):
    __tablename__ = "created_prompt"

    id = Column(UUID(as_uuid=False), primary_key=True)
    command = Column(String(64), nullable=False)
    user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_profile.id", ondelete="CASCADE"),
        nullable=False,
    )
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
    class_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_group.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_by_user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_profile.id", ondelete="CASCADE"),
        nullable=False,
    )
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

    class_room_id = Column(
        UUID(as_uuid=False),
        ForeignKey("class_room.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_profile.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)


class ClassReadReceipt(Base):
    __tablename__ = "class_read_receipt"

    class_room_id = Column(
        UUID(as_uuid=False),
        ForeignKey("class_room.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_profile.id", ondelete="CASCADE"),
        primary_key=True,
    )
    last_read_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)


class ClassMessage(Base):
    __tablename__ = "class_message"

    id = Column(UUID(as_uuid=False), primary_key=True)
    user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_profile.id", ondelete="CASCADE"),
        nullable=False,
    )
    class_room_id = Column(
        UUID(as_uuid=False),
        ForeignKey("class_room.id", ondelete="CASCADE"),
        nullable=False,
    )
    parent_id = Column(
        UUID(as_uuid=False),
        ForeignKey("class_message.id", ondelete="CASCADE"),
        nullable=True,
    )
    target_user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_profile.id", ondelete="CASCADE"),
        nullable=True,
    )
    content = Column(Text, nullable=False)
    data = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    meta = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)


class ClassMessageReaction(Base):
    __tablename__ = "class_message_reaction"

    id = Column(UUID(as_uuid=False), primary_key=True)
    user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_profile.id", ondelete="CASCADE"),
        nullable=False,
    )
    message_id = Column(
        UUID(as_uuid=False),
        ForeignKey("class_message.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(Text, nullable=False)
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)


class ClassAssistant(Base):
    __tablename__ = "class_assistant"

    id = Column(UUID(as_uuid=False), primary_key=True)
    class_room_id = Column(
        UUID(as_uuid=False),
        ForeignKey("class_room.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_by_user_id = Column(
        UUID(as_uuid=False), ForeignKey("user_profile.id"), nullable=False
    )
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

    class_room_id = Column(
        UUID(as_uuid=False),
        ForeignKey("class_room.id", ondelete="CASCADE"),
        primary_key=True,
    )
    library_id = Column(
        UUID(as_uuid=False),
        ForeignKey("library.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_by_user_id = Column(
        UUID(as_uuid=False), ForeignKey("user_profile.id"), nullable=False
    )
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)


class UserProfile(Base):
    __tablename__ = "user_profile"

    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name = Column(Text, nullable=True)
    email = Column(CITEXT, nullable=True)
    role = Column(Text, nullable=True)
    profile_image_url = Column(Text, nullable=True)
    last_active_at = Column(BigInteger, nullable=True)
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    api_key = Column(Text, nullable=True, unique=True)
    settings = Column(JSONB, nullable=True, server_default=text("'{}'::jsonb"))
    info = Column(JSONB, nullable=True, server_default=text("'{}'::jsonb"))
    oauth_sub = Column(Text, nullable=True, unique=True)


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
    session_nonce = Column(
        Text,
        nullable=False,
        server_default=text("encode(gen_random_bytes(16), 'hex')"),
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
    default_temperature = Column(
        Float(asdecimal=False), nullable=False, server_default=text("0.7")
    )
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
        UniqueConstraint(
            "provider", "subject", name="uq_user_identity_provider_subject"
        ),
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

    __table_args__ = (Index("idx_user_file_user", "user_id"),)


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
    items = Column(JSONB, nullable=True, server_default=text("'{}'::jsonb"))
    meta = Column(JSONB, nullable=True, server_default=text("'{}'::jsonb"))
    is_expanded = Column(Boolean, nullable=False, server_default=text("false"))
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

    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    owner_user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_profile.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    data = Column(JSONB, nullable=True, server_default=text("'{}'::jsonb"))
    meta = Column(JSONB, nullable=True, server_default=text("'{}'::jsonb"))
    created_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)
    updated_at = Column(BigInteger, nullable=False, server_default=_NOW_MS)

    __table_args__ = (
        Index(
            "ux_user_group_owner_name",
            "owner_user_id",
            func.lower(name),
            unique=True,
        ),
    )


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
