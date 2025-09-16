-- patch_sync_map_ddl.sql (v2)
BEGIN;

-- user_group_member
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='user_group_member') THEN
    EXECUTE $$
      CREATE TABLE user_group_member (
        group_id uuid NOT NULL REFERENCES user_group(id) ON DELETE CASCADE,
        user_id uuid NOT NULL REFERENCES user_profile(id) ON DELETE CASCADE,
        role_in_group text NOT NULL,
        created_at bigint NOT NULL DEFAULT now_ms(),
        PRIMARY KEY (group_id, user_id)
      );
    $$;
  END IF;
END $$;

-- created_tool_version: NOT NULL & unique composite
ALTER TABLE IF EXISTS created_tool_version
  ALTER COLUMN version SET NOT NULL,
  ALTER COLUMN content SET NOT NULL;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_indexes
    WHERE tablename='created_tool_version' AND indexname='ux_ctv_tool_version'
  ) THEN
    EXECUTE 'CREATE UNIQUE INDEX ux_ctv_tool_version ON created_tool_version(tool_id, version)';
  END IF;
END $$;

-- library.name NOT NULL
ALTER TABLE IF EXISTS library
  ALTER COLUMN name SET NOT NULL;

-- resource_shares: XOR check & unique index
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conrelid = 'resource_shares'::regclass
      AND contype = 'c'
      AND pg_get_constraintdef(oid) LIKE '%(grantee_group_id IS NULL)%<>(grantee_user_id IS NULL)%'
  ) THEN
    EXECUTE 'ALTER TABLE resource_shares ADD CONSTRAINT resource_shares_xor CHECK ( (grantee_group_id IS NULL) <> (grantee_user_id IS NULL) )';
  END IF;
END $$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_indexes
    WHERE tablename='resource_shares' AND indexname='ux_resource_share_target_grantee'
  ) THEN
    EXECUTE 'CREATE UNIQUE INDEX ux_resource_share_target_grantee ON resource_shares (resource_type, resource_id, grantee_group_id, grantee_user_id)';
  END IF;
END $$;

COMMIT;
