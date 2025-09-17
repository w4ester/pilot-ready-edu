
-- =====================================================================
-- database_schema_consolidated_v2.sql
-- RAG + Classroom Platform (Educator Lexicon) — Consolidated DDL (v2)
-- Includes user_group_member and constraint/index corrections.
-- =====================================================================

SET search_path = public;

-- Extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS citext;
CREATE EXTENSION IF NOT EXISTS vector;

-- Helpers
CREATE OR REPLACE FUNCTION now_ms() RETURNS bigint
LANGUAGE sql STABLE PARALLEL SAFE AS $$
  SELECT (extract(epoch from clock_timestamp())*1000)::bigint;
$$;

CREATE OR REPLACE FUNCTION set_updated_at() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  NEW.updated_at := now_ms();
  RETURN NEW;
END;
$$;

-- Types
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'resource_kind') THEN
    CREATE TYPE resource_kind AS ENUM ('tool','model','prompt','artifact','library','document');
  END IF;
END $$;

-- ===================== Identity & Auth =====================

CREATE TABLE IF NOT EXISTS user_profile (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text,
  email citext,
  role text,
  profile_image_url text,
  last_active_at bigint,
  created_at bigint NOT NULL DEFAULT now_ms(),
  updated_at bigint NOT NULL DEFAULT now_ms(),
  api_key text UNIQUE,
  settings jsonb DEFAULT '{}'::jsonb,
  info jsonb DEFAULT '{}'::jsonb,
  oauth_sub text UNIQUE
);
CREATE TRIGGER trg_user_profile_updated_at
  BEFORE UPDATE ON user_profile
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS user_auth (
  id uuid PRIMARY KEY REFERENCES user_profile(id) ON DELETE CASCADE,
  email citext UNIQUE NOT NULL,
  password text,
  is_active boolean NOT NULL DEFAULT true,
  created_at bigint NOT NULL DEFAULT now_ms(),
  updated_at bigint NOT NULL DEFAULT now_ms(),
  last_login_at bigint,
  failed_attempts integer NOT NULL DEFAULT 0,
  locked_until bigint,
  auth_method text NOT NULL DEFAULT 'password',
  requires_password_change boolean NOT NULL DEFAULT false
);
CREATE TRIGGER trg_user_auth_updated_at
  BEFORE UPDATE ON user_auth
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS user_settings (
  user_id uuid PRIMARY KEY REFERENCES user_profile(id) ON DELETE CASCADE,
  default_model varchar(100) NOT NULL DEFAULT 'gpt-oss:20B',
  default_temperature double precision NOT NULL DEFAULT 0.7,
  default_max_tokens integer NOT NULL DEFAULT 500,
  embedding_model varchar(100) NOT NULL DEFAULT 'embeddinggemma:300m',
  auto_save boolean NOT NULL DEFAULT true,
  auto_save_interval integer NOT NULL DEFAULT 30,
  theme varchar(20) NOT NULL DEFAULT 'light',
  preferences jsonb DEFAULT '{}'::jsonb,
  created_at bigint NOT NULL DEFAULT now_ms(),
  updated_at bigint NOT NULL DEFAULT now_ms()
);
CREATE TRIGGER trg_user_settings_updated_at
  BEFORE UPDATE ON user_settings
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS user_identity (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES user_profile(id) ON DELETE CASCADE,
  provider text NOT NULL,
  subject text NOT NULL,
  email citext,
  email_verified boolean NOT NULL DEFAULT false,
  raw_profile jsonb,
  is_primary boolean NOT NULL DEFAULT false,
  connected_at bigint NOT NULL DEFAULT now_ms(),
  last_login_at bigint,
  created_at bigint NOT NULL DEFAULT now_ms(),
  updated_at bigint NOT NULL DEFAULT now_ms(),
  UNIQUE (provider, subject)
);
CREATE TRIGGER trg_user_identity_updated_at
  BEFORE UPDATE ON user_identity
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS organization (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  slug text UNIQUE,
  meta jsonb DEFAULT '{}'::jsonb,
  created_at bigint NOT NULL DEFAULT now_ms(),
  updated_at bigint NOT NULL DEFAULT now_ms()
);
CREATE TRIGGER trg_organization_updated_at
  BEFORE UPDATE ON organization
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS organization_domain (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id uuid NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
  domain text NOT NULL,
  verified boolean NOT NULL DEFAULT false,
  created_at bigint NOT NULL DEFAULT now_ms(),
  updated_at bigint NOT NULL DEFAULT now_ms()
);
CREATE TRIGGER trg_organization_domain_updated_at
  BEFORE UPDATE ON organization_domain
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE UNIQUE INDEX IF NOT EXISTS ux_org_domain_lower
  ON organization_domain (lower(domain));

CREATE TABLE IF NOT EXISTS organization_idp (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id uuid NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
  provider text NOT NULL,
  config jsonb NOT NULL,
  is_enabled boolean NOT NULL DEFAULT true,
  created_at bigint NOT NULL DEFAULT now_ms(),
  updated_at bigint NOT NULL DEFAULT now_ms()
);
CREATE TRIGGER trg_organization_idp_updated_at
  BEFORE UPDATE ON organization_idp
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE UNIQUE INDEX IF NOT EXISTS ux_org_provider_lower
  ON organization_idp (organization_id, lower(provider));

-- ===================== Classroom =====================

CREATE TABLE IF NOT EXISTS user_group (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_user_id uuid NOT NULL REFERENCES user_profile(id) ON DELETE CASCADE,
  name text NOT NULL,
  description text,
  data jsonb DEFAULT '{}'::jsonb,
  meta jsonb DEFAULT '{}'::jsonb,
  created_at bigint NOT NULL DEFAULT now_ms(),
  updated_at bigint NOT NULL DEFAULT now_ms()
);
CREATE TRIGGER trg_user_group_updated_at
  BEFORE UPDATE ON user_group
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE UNIQUE INDEX IF NOT EXISTS ux_user_group_owner_name
  ON user_group (owner_user_id, lower(name));

-- NEW in v2: user_group_member (used by RLS)
CREATE TABLE IF NOT EXISTS user_group_member (
  group_id uuid NOT NULL REFERENCES user_group(id) ON DELETE CASCADE,
  user_id uuid NOT NULL REFERENCES user_profile(id) ON DELETE CASCADE,
  role_in_group text NOT NULL,
  created_at bigint NOT NULL DEFAULT now_ms(),
  PRIMARY KEY (group_id, user_id)
);

CREATE TABLE IF NOT EXISTS class_room (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  class_id uuid NOT NULL REFERENCES user_group(id) ON DELETE CASCADE,
  created_by_user_id uuid NOT NULL REFERENCES user_profile(id),
  name text NOT NULL,
  channel_type text,
  description text,
  data jsonb DEFAULT '{}'::jsonb,
  meta jsonb DEFAULT '{}'::jsonb,
  access_control jsonb DEFAULT '{}'::jsonb,
  is_archived boolean NOT NULL DEFAULT false,
  created_at bigint NOT NULL DEFAULT now_ms(),
  updated_at bigint NOT NULL DEFAULT now_ms()
);
CREATE TRIGGER trg_class_room_updated_at
  BEFORE UPDATE ON class_room
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE UNIQUE INDEX IF NOT EXISTS ux_class_room_class_name
  ON class_room (class_id, lower(name));
CREATE INDEX IF NOT EXISTS idx_class_room_class ON class_room(class_id);

CREATE TABLE IF NOT EXISTS class_room_member (
  class_room_id uuid NOT NULL REFERENCES class_room(id) ON DELETE CASCADE,
  user_id uuid NOT NULL REFERENCES user_profile(id) ON DELETE CASCADE,
  created_at bigint NOT NULL DEFAULT now_ms(),
  PRIMARY KEY (class_room_id, user_id)
);

CREATE TABLE IF NOT EXISTS class_read_receipt (
  class_room_id uuid NOT NULL REFERENCES class_room(id) ON DELETE CASCADE,
  user_id uuid NOT NULL REFERENCES user_profile(id) ON DELETE CASCADE,
  last_read_at bigint NOT NULL DEFAULT now_ms(),
  PRIMARY KEY (class_room_id, user_id)
);
CREATE INDEX IF NOT EXISTS idx_class_read_receipt_user ON class_read_receipt(user_id);

-- ===================== Personal Chats & Organization =====================

CREATE TABLE IF NOT EXISTS user_folder (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  parent_id uuid REFERENCES user_folder(id) ON DELETE CASCADE,
  user_id uuid NOT NULL REFERENCES user_profile(id) ON DELETE CASCADE,
  name text NOT NULL,
  items jsonb DEFAULT '{}'::jsonb,
  meta jsonb DEFAULT '{}'::jsonb,
  is_expanded boolean NOT NULL DEFAULT false,
  created_at bigint NOT NULL DEFAULT now_ms(),
  updated_at bigint NOT NULL DEFAULT now_ms()
);
CREATE TRIGGER trg_user_folder_updated_at
  BEFORE UPDATE ON user_folder
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS user_chat (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES user_profile(id) ON DELETE CASCADE,
  title text,
  conversation jsonb NOT NULL,
  share_id text UNIQUE,
  archived boolean NOT NULL DEFAULT false,
  pinned boolean DEFAULT false,
  meta jsonb DEFAULT '{}'::jsonb,
  folder_id uuid REFERENCES user_folder(id) ON DELETE SET NULL,
  created_at bigint NOT NULL DEFAULT now_ms(),
  updated_at bigint NOT NULL DEFAULT now_ms()
);
CREATE TRIGGER trg_user_chat_updated_at
  BEFORE UPDATE ON user_chat
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS user_chat_tag (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tag_name text NOT NULL,
  chat_id uuid NOT NULL REFERENCES user_chat(id) ON DELETE CASCADE,
  user_id uuid NOT NULL REFERENCES user_profile(id) ON DELETE CASCADE,
  created_at bigint NOT NULL DEFAULT now_ms()
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_user_chat_tag_user_chat_name
  ON user_chat_tag (user_id, chat_id, lower(tag_name));

CREATE TABLE IF NOT EXISTS user_tag (
  id text NOT NULL,
  name text NOT NULL,
  user_id uuid NOT NULL REFERENCES user_profile(id) ON DELETE CASCADE,
  meta jsonb DEFAULT '{}'::jsonb,
  PRIMARY KEY (id, user_id)
);

-- ===================== Files & RAG (pgvector) =====================

CREATE TABLE IF NOT EXISTS user_file (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES user_profile(id) ON DELETE CASCADE,
  hash text,
  filename text NOT NULL,
  path text,
  data jsonb DEFAULT '{}'::jsonb,
  meta jsonb DEFAULT '{}'::jsonb,
  access_control jsonb DEFAULT '{}'::jsonb,
  created_at bigint NOT NULL DEFAULT now_ms(),
  updated_at bigint NOT NULL DEFAULT now_ms()
);
CREATE INDEX IF NOT EXISTS idx_user_file_user ON user_file(user_id);
CREATE TRIGGER trg_user_file_updated_at
  BEFORE UPDATE ON user_file
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS library (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES user_profile(id) ON DELETE CASCADE,
  name text NOT NULL,
  description text,
  data jsonb DEFAULT '{}'::jsonb,
  meta jsonb DEFAULT '{}'::jsonb,
  access_control jsonb DEFAULT '{}'::jsonb,
  created_at bigint NOT NULL DEFAULT now_ms(),
  updated_at bigint NOT NULL DEFAULT now_ms()
);
CREATE INDEX IF NOT EXISTS idx_library_user ON library(user_id);
CREATE TRIGGER trg_library_updated_at
  BEFORE UPDATE ON library
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS library_document (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  library_id uuid NOT NULL REFERENCES library(id) ON DELETE CASCADE,
  source text,
  uri text,
  title text,
  meta jsonb DEFAULT '{}'::jsonb,
  created_at bigint NOT NULL DEFAULT now_ms(),
  updated_at bigint NOT NULL DEFAULT now_ms()
);
CREATE INDEX IF NOT EXISTS idx_library_document_library ON library_document(library_id);
CREATE TRIGGER trg_library_document_updated_at
  BEFORE UPDATE ON library_document
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS document_chunk (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id uuid NOT NULL REFERENCES library_document(id) ON DELETE CASCADE,
  chunk_index integer NOT NULL CHECK (chunk_index >= 0),
  content text NOT NULL,
  embedding vector(768) NOT NULL,
  token_count integer,
  meta jsonb,
  created_at bigint NOT NULL DEFAULT now_ms(),
  content_tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', coalesce(content, ''))) STORED
);
CREATE INDEX IF NOT EXISTS idx_document_chunk_doc ON document_chunk(document_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_document_chunk_unique ON document_chunk(document_id, chunk_index);
CREATE INDEX IF NOT EXISTS idx_document_chunk_embedding_hnsw
  ON document_chunk USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_document_chunk_tsv_gin
  ON document_chunk USING gin (content_tsv);

CREATE TABLE IF NOT EXISTS library_file (
  library_id uuid NOT NULL REFERENCES library(id) ON DELETE CASCADE,
  file_id uuid NOT NULL REFERENCES user_file(id) ON DELETE CASCADE,
  created_at bigint NOT NULL DEFAULT now_ms(),
  PRIMARY KEY (library_id, file_id)
);
CREATE INDEX IF NOT EXISTS idx_library_file_file ON library_file(file_id);

-- ===================== Creation (Tools, Models, Prompts) =====================

CREATE TABLE IF NOT EXISTS created_tool (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES user_profile(id) ON DELETE CASCADE,
  name text NOT NULL,
  slug text NOT NULL,
  language text NOT NULL DEFAULT 'python',
  entrypoint text,
  content text NOT NULL,
  requirements text,
  sandbox_profile text NOT NULL DEFAULT 'restricted',
  timeout_ms integer NOT NULL DEFAULT 60000 CHECK (timeout_ms BETWEEN 1 AND 600000),
  memory_limit_mb integer NOT NULL DEFAULT 512 CHECK (memory_limit_mb BETWEEN 64 AND 8192),
  meta jsonb DEFAULT '{}'::jsonb,
  valves jsonb DEFAULT '{}'::jsonb,
  access_control jsonb DEFAULT '{}'::jsonb,
  is_active boolean NOT NULL DEFAULT true,
  created_at bigint NOT NULL DEFAULT now_ms(),
  updated_at bigint NOT NULL DEFAULT now_ms(),
  CHECK (language IN ('python')),
  CHECK (sandbox_profile IN ('restricted','networked','gpu'))
);
CREATE INDEX IF NOT EXISTS idx_created_tool_user ON created_tool(user_id);
CREATE UNIQUE INDEX IF NOT EXISTS ux_created_tool_owner_slug
  ON created_tool (user_id, lower(slug));
CREATE TRIGGER trg_created_tool_updated_at
  BEFORE UPDATE ON created_tool
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS created_tool_version (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tool_id uuid NOT NULL REFERENCES created_tool(id) ON DELETE CASCADE,
  version integer NOT NULL,
  content text NOT NULL,
  requirements text,
  meta jsonb DEFAULT '{}'::jsonb,
  created_at bigint NOT NULL DEFAULT now_ms(),
  UNIQUE (tool_id, version)
);

CREATE TABLE IF NOT EXISTS created_model (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES user_profile(id) ON DELETE CASCADE,
  base_model_id text,
  name text NOT NULL,
  params jsonb DEFAULT '{}'::jsonb,
  meta jsonb DEFAULT '{}'::jsonb,
  access_control jsonb DEFAULT '{}'::jsonb,
  is_active boolean NOT NULL DEFAULT true,
  created_at bigint NOT NULL DEFAULT now_ms(),
  updated_at bigint NOT NULL DEFAULT now_ms()
);
CREATE TRIGGER trg_created_model_updated_at
  BEFORE UPDATE ON created_model
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE UNIQUE INDEX IF NOT EXISTS ux_created_model_owner_name
  ON created_model (user_id, lower(name));

CREATE TABLE IF NOT EXISTS model_tool (
  model_id uuid NOT NULL REFERENCES created_model(id) ON DELETE CASCADE,
  tool_id uuid NOT NULL REFERENCES created_tool(id) ON DELETE CASCADE,
  order_index integer,
  config jsonb DEFAULT '{}'::jsonb,
  enabled boolean NOT NULL DEFAULT true,
  PRIMARY KEY (model_id, tool_id)
);
CREATE INDEX IF NOT EXISTS idx_model_tool_tool ON model_tool(tool_id);

CREATE TABLE IF NOT EXISTS model_library (
  model_id uuid NOT NULL REFERENCES created_model(id) ON DELETE CASCADE,
  library_id uuid NOT NULL REFERENCES library(id) ON DELETE CASCADE,
  order_index integer,
  retrieval jsonb DEFAULT '{}'::jsonb,
  PRIMARY KEY (model_id, library_id)
);
CREATE INDEX IF NOT EXISTS idx_model_library_library ON model_library(library_id);

CREATE TABLE IF NOT EXISTS created_prompt (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  command varchar(64) NOT NULL,
  user_id uuid NOT NULL REFERENCES user_profile(id) ON DELETE CASCADE,
  title text,
  content text NOT NULL,
  variables jsonb DEFAULT '{}'::jsonb,
  access_control jsonb DEFAULT '{}'::jsonb,
  created_at bigint NOT NULL DEFAULT now_ms(),
  updated_at bigint NOT NULL DEFAULT now_ms(),
  CHECK (command ~ '^/')
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_created_prompt_user_cmd
  ON created_prompt (user_id, lower(command));
CREATE TRIGGER trg_created_prompt_updated_at
  BEFORE UPDATE ON created_prompt
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ===================== Classroom Content & Assistants =====================

CREATE TABLE IF NOT EXISTS class_message (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES user_profile(id) ON DELETE CASCADE,
  class_room_id uuid NOT NULL REFERENCES class_room(id) ON DELETE CASCADE,
  parent_id uuid REFERENCES class_message(id) ON DELETE CASCADE,
  target_user_id uuid REFERENCES user_profile(id) ON DELETE CASCADE,
  content text NOT NULL,
  data jsonb DEFAULT '{}'::jsonb,
  meta jsonb DEFAULT '{}'::jsonb,
  created_at bigint NOT NULL DEFAULT now_ms(),
  updated_at bigint NOT NULL DEFAULT now_ms()
);
CREATE INDEX IF NOT EXISTS idx_class_message_room ON class_message(class_room_id);
CREATE TRIGGER trg_class_message_updated_at
  BEFORE UPDATE ON class_message
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS class_message_reaction (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES user_profile(id) ON DELETE CASCADE,
  message_id uuid NOT NULL REFERENCES class_message(id) ON DELETE CASCADE,
  name text NOT NULL,
  created_at bigint NOT NULL DEFAULT now_ms(),
  UNIQUE (message_id, user_id, name)
);

CREATE TABLE IF NOT EXISTS class_assistant (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  class_room_id uuid NOT NULL REFERENCES class_room(id) ON DELETE CASCADE,
  created_by_user_id uuid NOT NULL REFERENCES user_profile(id),
  model_id text NOT NULL,
  name text,
  system_prompt text,
  temperature numeric NOT NULL DEFAULT 0.7 CHECK (temperature >= 0 AND temperature <= 2),
  invocation_mode text NOT NULL DEFAULT 'manual' CHECK (invocation_mode IN ('manual','on_mention','auto')),
  tool_config jsonb DEFAULT '{}'::jsonb,
  is_active boolean NOT NULL DEFAULT true,
  created_at bigint NOT NULL DEFAULT now_ms(),
  updated_at bigint NOT NULL DEFAULT now_ms()
);
CREATE INDEX IF NOT EXISTS idx_class_assistant_room ON class_assistant(class_room_id);
CREATE TRIGGER trg_class_assistant_updated_at
  BEFORE UPDATE ON class_assistant
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS class_knowledge (
  class_room_id uuid NOT NULL REFERENCES class_room(id) ON DELETE CASCADE,
  library_id uuid NOT NULL REFERENCES library(id) ON DELETE CASCADE,
  created_by_user_id uuid NOT NULL REFERENCES user_profile(id),
  created_at bigint NOT NULL DEFAULT now_ms(),
  PRIMARY KEY (class_room_id, library_id)
);

-- ===================== Artifacts & Sharing =====================

CREATE TABLE IF NOT EXISTS user_artifact (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES user_profile(id) ON DELETE CASCADE,
  chat_id uuid REFERENCES user_chat(id) ON DELETE SET NULL,
  group_id uuid REFERENCES user_group(id) ON DELETE SET NULL,
  title text NOT NULL,
  type text NOT NULL,
  language text,
  content text NOT NULL,
  subject_area text,
  grade_level text,
  version integer NOT NULL DEFAULT 1 CHECK (version >= 1),
  parent_artifact_id uuid REFERENCES user_artifact(id) ON DELETE SET NULL,
  meta jsonb DEFAULT '{}'::jsonb,
  access_control jsonb DEFAULT '{}'::jsonb,
  is_published boolean NOT NULL DEFAULT false,
  is_template boolean NOT NULL DEFAULT false,
  created_at bigint NOT NULL DEFAULT now_ms(),
  updated_at bigint NOT NULL DEFAULT now_ms()
);
CREATE TRIGGER trg_user_artifact_updated_at
  BEFORE UPDATE ON user_artifact
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE UNIQUE INDEX IF NOT EXISTS ux_user_artifact_lineage_version
  ON user_artifact (COALESCE(parent_artifact_id, id), version);

CREATE TABLE IF NOT EXISTS resource_shares (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  resource_type resource_kind NOT NULL,
  resource_id uuid NOT NULL,
  grantee_group_id uuid REFERENCES user_group(id) ON DELETE CASCADE,
  grantee_user_id uuid REFERENCES user_profile(id) ON DELETE CASCADE,
  permission text NOT NULL CHECK (permission IN ('view','use','edit','admin')),
  created_by uuid NOT NULL REFERENCES user_profile(id) ON DELETE CASCADE,
  created_at bigint NOT NULL DEFAULT now_ms(),
  expires_at bigint,
  CHECK ( (grantee_group_id IS NULL) <> (grantee_user_id IS NULL) )
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_resource_share_target_grantee
  ON resource_shares (resource_type, resource_id, grantee_group_id, grantee_user_id);

-- Compat view for artifact shares
CREATE OR REPLACE VIEW group_artifact_access AS
SELECT
  rs.grantee_group_id AS group_id,
  rs.resource_id      AS artifact_id,
  'group_ui'::text    AS scope,
  rs.created_by       AS granted_by,
  rs.created_at
FROM resource_shares rs
WHERE rs.resource_type = 'artifact' AND rs.grantee_group_id IS NOT NULL;

-- ===================== Feedback, Memory, App Config =====================

CREATE TABLE IF NOT EXISTS user_feedback (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES user_profile(id) ON DELETE CASCADE,
  version bigint NOT NULL DEFAULT 0,
  type text NOT NULL,
  data jsonb,
  meta jsonb,
  snapshot jsonb,
  created_at bigint NOT NULL DEFAULT now_ms(),
  updated_at bigint NOT NULL DEFAULT now_ms()
);
CREATE TRIGGER trg_user_feedback_updated_at
  BEFORE UPDATE ON user_feedback
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS user_memory (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES user_profile(id) ON DELETE CASCADE,
  content text NOT NULL,
  created_at bigint NOT NULL DEFAULT now_ms(),
  updated_at bigint NOT NULL DEFAULT now_ms()
);
CREATE TRIGGER trg_user_memory_updated_at
  BEFORE UPDATE ON user_memory
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS app_config (
  id integer PRIMARY KEY,
  data jsonb NOT NULL,
  version integer NOT NULL,
  created_at bigint NOT NULL DEFAULT now_ms(),
  updated_at bigint NOT NULL DEFAULT now_ms()
);
CREATE TRIGGER trg_app_config_updated_at
  BEFORE UPDATE ON app_config
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ===================== BYOM Registry =====================

CREATE TABLE IF NOT EXISTS model_provider (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text UNIQUE NOT NULL,
  kind text NOT NULL,
  config jsonb DEFAULT '{}'::jsonb,
  created_at bigint NOT NULL DEFAULT now_ms(),
  updated_at bigint NOT NULL DEFAULT now_ms()
);
CREATE TRIGGER trg_model_provider_updated_at
  BEFORE UPDATE ON model_provider
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS base_model (
  id text PRIMARY KEY,
  provider_id uuid NOT NULL REFERENCES model_provider(id) ON DELETE CASCADE,
  modality text NOT NULL,
  embedding_dim integer,
  meta jsonb DEFAULT '{}'::jsonb,
  created_at bigint NOT NULL DEFAULT now_ms(),
  updated_at bigint NOT NULL DEFAULT now_ms()
);
CREATE INDEX IF NOT EXISTS idx_base_model_provider ON base_model(provider_id);
CREATE TRIGGER trg_base_model_updated_at
  BEFORE UPDATE ON base_model
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS provider_credential (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES user_profile(id) ON DELETE CASCADE,
  organization_id uuid REFERENCES organization(id) ON DELETE CASCADE,
  provider_id uuid NOT NULL REFERENCES model_provider(id) ON DELETE CASCADE,
  name text NOT NULL,
  secret_ref text NOT NULL,
  created_at bigint NOT NULL DEFAULT now_ms(),
  updated_at bigint NOT NULL DEFAULT now_ms()
);
CREATE INDEX IF NOT EXISTS idx_provider_credential_provider ON provider_credential(provider_id);
CREATE INDEX IF NOT EXISTS idx_provider_credential_user ON provider_credential(user_id);
CREATE INDEX IF NOT EXISTS idx_provider_credential_org ON provider_credential(organization_id);
CREATE TRIGGER trg_provider_credential_updated_at
  BEFORE UPDATE ON provider_credential
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ===================== MCP (Model Context Protocol) =====================

CREATE TABLE IF NOT EXISTS mcp_server (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_user_id uuid REFERENCES user_profile(id) ON DELETE CASCADE,
  organization_id uuid REFERENCES organization(id) ON DELETE CASCADE,
  name text NOT NULL,
  slug text,
  transport text NOT NULL CHECK (transport IN ('stdio','sse')),
  command text,
  args jsonb,
  env jsonb,
  working_dir text,
  sse_url text,
  headers jsonb,
  auth_kind text NOT NULL DEFAULT 'none' CHECK (auth_kind IN ('none','bearer','basic','header')),
  credential_id uuid REFERENCES provider_credential(id) ON DELETE SET NULL,
  timeouts jsonb,
  is_enabled boolean NOT NULL DEFAULT true,
  health_status text NOT NULL DEFAULT 'unknown' CHECK (health_status IN ('unknown','healthy','unreachable','error')),
  last_seen_at bigint,
  last_error text,
  provider_kind text NOT NULL DEFAULT 'external' CHECK (provider_kind IN ('internal','external')),
  is_verified_provider boolean NOT NULL DEFAULT false,
  certification jsonb,
  meta jsonb,
  created_at bigint NOT NULL DEFAULT now_ms(),
  updated_at bigint NOT NULL DEFAULT now_ms()
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_mcp_server_owner_slug
  ON mcp_server(owner_user_id, lower(coalesce(slug, name)));
CREATE INDEX IF NOT EXISTS idx_mcp_server_org ON mcp_server(organization_id);
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'trg_mcp_server_updated_at'
  ) THEN
    CREATE TRIGGER trg_mcp_server_updated_at
      BEFORE UPDATE ON mcp_server
      FOR EACH ROW EXECUTE FUNCTION set_updated_at();
  END IF;
END $$;

CREATE TABLE IF NOT EXISTS mcp_server_tool (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  server_id uuid NOT NULL REFERENCES mcp_server(id) ON DELETE CASCADE,
  name text NOT NULL,
  description text,
  input_schema jsonb NOT NULL,
  is_enabled boolean NOT NULL DEFAULT true,
  last_discovered_at bigint NOT NULL DEFAULT now_ms(),
  created_at bigint NOT NULL DEFAULT now_ms()
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_mcp_server_tool_name
  ON mcp_server_tool(server_id, lower(name));
CREATE INDEX IF NOT EXISTS idx_mcp_server_tool_server
  ON mcp_server_tool(server_id);

CREATE TABLE IF NOT EXISTS model_mcp_tool (
  model_id uuid NOT NULL REFERENCES created_model(id) ON DELETE CASCADE,
  server_id uuid NOT NULL REFERENCES mcp_server(id) ON DELETE CASCADE,
  tool_name text NOT NULL,
  order_index integer,
  config jsonb,
  enabled boolean NOT NULL DEFAULT true,
  created_at bigint NOT NULL DEFAULT now_ms(),
  PRIMARY KEY (model_id, server_id, tool_name)
);
CREATE INDEX IF NOT EXISTS idx_model_mcp_tool_server
  ON model_mcp_tool(server_id);

CREATE TABLE IF NOT EXISTS mcp_server_version (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  server_id uuid NOT NULL REFERENCES mcp_server(id) ON DELETE CASCADE,
  version integer NOT NULL,
  spec jsonb NOT NULL,
  created_at bigint NOT NULL DEFAULT now_ms(),
  UNIQUE (server_id, version)
);

CREATE TABLE IF NOT EXISTS mcp_server_binding (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  server_id uuid NOT NULL REFERENCES mcp_server(id) ON DELETE CASCADE,
  organization_id uuid REFERENCES organization(id) ON DELETE CASCADE,
  class_room_id uuid REFERENCES class_room(id) ON DELETE CASCADE,
  model_id uuid REFERENCES created_model(id) ON DELETE CASCADE,
  assistant_id uuid REFERENCES class_assistant(id) ON DELETE CASCADE,
  enabled boolean NOT NULL DEFAULT true,
  precedence integer NOT NULL DEFAULT 0,
  created_at bigint NOT NULL DEFAULT now_ms(),
  updated_at bigint NOT NULL DEFAULT now_ms(),
  CHECK (
    ((organization_id IS NOT NULL)::int +
     (class_room_id IS NOT NULL)::int +
     (model_id IS NOT NULL)::int +
     (assistant_id IS NOT NULL)::int) <= 1
  )
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_mcp_server_binding_scope
  ON mcp_server_binding(server_id, organization_id, class_room_id, model_id, assistant_id);
CREATE INDEX IF NOT EXISTS idx_mcp_server_binding_server
  ON mcp_server_binding(server_id);
CREATE INDEX IF NOT EXISTS idx_mcp_server_binding_prec
  ON mcp_server_binding(server_id, precedence DESC);
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'trg_mcp_server_binding_updated_at'
  ) THEN
    CREATE TRIGGER trg_mcp_server_binding_updated_at
      BEFORE UPDATE ON mcp_server_binding
      FOR EACH ROW EXECUTE FUNCTION set_updated_at();
  END IF;
END $$;

-- ===================== Platform Capabilities =====================

CREATE TABLE IF NOT EXISTS platform_capability (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  key text NOT NULL,
  description text,
  rollout_phase text NOT NULL DEFAULT 'experimental' CHECK (rollout_phase IN ('experimental','beta','ga','deprecated')),
  guardrails jsonb,
  meta jsonb,
  created_at bigint NOT NULL DEFAULT now_ms(),
  updated_at bigint NOT NULL DEFAULT now_ms()
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_platform_capability_key
  ON platform_capability(lower(key));
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'trg_platform_capability_updated_at'
  ) THEN
    CREATE TRIGGER trg_platform_capability_updated_at
      BEFORE UPDATE ON platform_capability
      FOR EACH ROW EXECUTE FUNCTION set_updated_at();
  END IF;
END $$;

CREATE TABLE IF NOT EXISTS platform_capability_scope (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  capability_id uuid NOT NULL REFERENCES platform_capability(id) ON DELETE CASCADE,
  organization_id uuid REFERENCES organization(id) ON DELETE CASCADE,
  class_room_id uuid REFERENCES class_room(id) ON DELETE CASCADE,
  model_id uuid REFERENCES created_model(id) ON DELETE CASCADE,
  assistant_id uuid REFERENCES class_assistant(id) ON DELETE CASCADE,
  scope_label text,
  enabled boolean NOT NULL DEFAULT true,
  precedence integer NOT NULL DEFAULT 0,
  config jsonb,
  starts_at bigint,
  ends_at bigint,
  created_by uuid REFERENCES user_profile(id) ON DELETE SET NULL,
  created_at bigint NOT NULL DEFAULT now_ms(),
  updated_at bigint NOT NULL DEFAULT now_ms(),
  CHECK (
    ((organization_id IS NOT NULL)::int +
     (class_room_id IS NOT NULL)::int +
     (model_id IS NOT NULL)::int +
     (assistant_id IS NOT NULL)::int) <= 1
  )
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_platform_capability_scope
  ON platform_capability_scope(capability_id, organization_id, class_room_id, model_id, assistant_id);
CREATE INDEX IF NOT EXISTS idx_platform_capability_scope_cap
  ON platform_capability_scope(capability_id);
CREATE INDEX IF NOT EXISTS idx_platform_capability_scope_prec
  ON platform_capability_scope(capability_id, precedence DESC);
CREATE INDEX IF NOT EXISTS idx_platform_capability_scope_org
  ON platform_capability_scope(organization_id) WHERE organization_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_platform_capability_scope_room
  ON platform_capability_scope(class_room_id) WHERE class_room_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_platform_capability_scope_model
  ON platform_capability_scope(model_id) WHERE model_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_platform_capability_scope_assistant
  ON platform_capability_scope(assistant_id) WHERE assistant_id IS NOT NULL;
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'trg_platform_capability_scope_updated_at'
  ) THEN
    CREATE TRIGGER trg_platform_capability_scope_updated_at
      BEFORE UPDATE ON platform_capability_scope
      FOR EACH ROW EXECUTE FUNCTION set_updated_at();
  END IF;
END $$;

CREATE TABLE IF NOT EXISTS model_capability (
  model_id uuid NOT NULL REFERENCES created_model(id) ON DELETE CASCADE,
  capability_id uuid NOT NULL REFERENCES platform_capability(id) ON DELETE CASCADE,
  enabled boolean NOT NULL DEFAULT true,
  precedence integer NOT NULL DEFAULT 0,
  config jsonb,
  created_at bigint NOT NULL DEFAULT now_ms(),
  PRIMARY KEY (model_id, capability_id)
);
CREATE INDEX IF NOT EXISTS idx_model_capability_cap
  ON model_capability(capability_id);

CREATE TABLE IF NOT EXISTS platform_feature_flag (
  key text PRIMARY KEY,
  is_enabled boolean NOT NULL DEFAULT false,
  effective_at bigint,
  sticky boolean NOT NULL DEFAULT false,
  description text,
  meta jsonb,
  created_at bigint NOT NULL DEFAULT now_ms(),
  updated_at bigint NOT NULL DEFAULT now_ms()
);
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'trg_platform_feature_flag_updated_at'
  ) THEN
    CREATE TRIGGER trg_platform_feature_flag_updated_at
      BEFORE UPDATE ON platform_feature_flag
      FOR EACH ROW EXECUTE FUNCTION set_updated_at();
  END IF;
END $$;

-- ===================== RLS Baseline =====================

ALTER TABLE IF EXISTS user_chat ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies WHERE schemaname='public' AND tablename='user_chat' AND policyname='user_chat_owner_only'
  ) THEN
    CREATE POLICY user_chat_owner_only ON user_chat
      USING (user_id = current_setting('app.user_id', true)::uuid);
  END IF;
END $$;

ALTER TABLE IF EXISTS user_file ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies WHERE schemaname='public' AND tablename='user_file' AND policyname='user_file_owner_only'
  ) THEN
    CREATE POLICY user_file_owner_only ON user_file
      USING (user_id = current_setting('app.user_id', true)::uuid);
  END IF;
END $$;

ALTER TABLE IF EXISTS class_room ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies WHERE schemaname='public' AND tablename='class_room' AND policyname='class_room_read'
  ) THEN
    CREATE POLICY class_room_read ON class_room
      USING (EXISTS (
        SELECT 1 FROM user_group_member m
        WHERE m.group_id = class_room.class_id
          AND m.user_id  = current_setting('app.user_id', true)::uuid
      ));
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies WHERE schemaname='public' AND tablename='class_room' AND policyname='class_room_write'
  ) THEN
    CREATE POLICY class_room_write ON class_room
      FOR UPDATE TO PUBLIC
      USING (EXISTS (
        SELECT 1 FROM user_group_member m
        WHERE m.group_id = class_room.class_id
          AND m.user_id  = current_setting('app.user_id', true)::uuid
          AND m.role_in_group IN ('teacher','assistant')
      ));
  END IF;
END $$;

-- ===================== Notes =====================
-- After bulk inserting into document_chunk, run ANALYZE.
-- Consider HNSW for larger corpora.
