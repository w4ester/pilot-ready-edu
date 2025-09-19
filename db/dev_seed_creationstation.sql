-- db/dev_seed_creationstation.sql
-- Seed data so Creation Station pages have content immediately.

-- Seed teacher (for DEV_USER_ID convenience)
INSERT INTO user_profile (id, name, email, role, created_at, updated_at)
VALUES ('99999999-9999-9999-9999-999999999999', 'Seed Teacher', 'seed.teacher@example.edu', 'teacher', now_ms(), now_ms())
ON CONFLICT (id) DO NOTHING;

INSERT INTO user_auth (id, email, password, is_active, created_at, updated_at)
VALUES ('99999999-9999-9999-9999-999999999999', 'seed.teacher@example.edu', NULL, true, now_ms(), now_ms())
ON CONFLICT (id) DO NOTHING;

-- Library sample
INSERT INTO library (id, user_id, name, description, created_at, updated_at)
VALUES (
  '11111111-1111-1111-1111-111111111111',
  '99999999-9999-9999-9999-999999999999',
  'Sample Library',
  'Demo content',
  now_ms(),
  now_ms()
)
ON CONFLICT (id) DO NOTHING;

-- Tool + immutable version 1
INSERT INTO created_tool (
  id, user_id, slug, name, language, entrypoint, content,
  requirements, sandbox_profile, timeout_ms, memory_limit_mb,
  valves, meta, access_control, created_at, updated_at
)
VALUES (
  '22222222-2222-2222-2222-222222222222',
  '99999999-9999-9999-9999-999999999999',
  'summarize_tool',
  'Summarize Tool',
  'python',
  'run',
  'def run(input):\n    return input',
  NULL,
  'restricted',
  60000,
  512,
  '{}'::jsonb,
  '{}'::jsonb,
  '{}'::jsonb,
  now_ms(),
  now_ms()
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO created_tool_version (id, tool_id, version, content, requirements, meta, created_at)
VALUES (
  '33333333-3333-3333-3333-333333333333',
  '22222222-2222-2222-2222-222222222222',
  1,
  'def run(input):\n    return input',
  NULL,
  '{}'::jsonb,
  now_ms()
)
ON CONFLICT (id) DO NOTHING;

-- Model sample
INSERT INTO created_model (
  id, user_id, base_model_id, name, params, meta, access_control,
  is_active, created_at, updated_at
)
VALUES (
  '44444444-4444-4444-4444-444444444444',
  '99999999-9999-9999-9999-999999999999',
  'gpt-oss:20B',
  'ELA-Planner',
  '{"temperature": 0.7}'::jsonb,
  '{}'::jsonb,
  '{}'::jsonb,
  true,
  now_ms(),
  now_ms()
)
ON CONFLICT (id) DO NOTHING;
