-- patch_add_mcp.sql
BEGIN;

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

DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.tables
    WHERE table_name = 'mcp_server'
  ) THEN
    IF NOT EXISTS (
      SELECT 1 FROM information_schema.columns
      WHERE table_name = 'mcp_server' AND column_name = 'provider_kind'
    ) THEN
      EXECUTE $$
        ALTER TABLE mcp_server
        ADD COLUMN provider_kind text NOT NULL DEFAULT 'external'
          CHECK (provider_kind IN ('internal','external'))
      $$;
    END IF;

    IF NOT EXISTS (
      SELECT 1 FROM information_schema.columns
      WHERE table_name = 'mcp_server' AND column_name = 'is_verified_provider'
    ) THEN
      EXECUTE $$
        ALTER TABLE mcp_server
        ADD COLUMN is_verified_provider boolean NOT NULL DEFAULT false
      $$;
    END IF;

    IF NOT EXISTS (
      SELECT 1 FROM information_schema.columns
      WHERE table_name = 'mcp_server' AND column_name = 'certification'
    ) THEN
      EXECUTE $$
        ALTER TABLE mcp_server
        ADD COLUMN certification jsonb
      $$;
    END IF;
  END IF;
END $$;

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

COMMIT;
