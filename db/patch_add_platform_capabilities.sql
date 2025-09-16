-- patch_add_platform_capabilities.sql
BEGIN;

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

COMMIT;
