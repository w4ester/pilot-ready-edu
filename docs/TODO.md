# TODO

## Database & Backend Naming Consistency
- [ ] **PRIORITY**: Revisit database table names and backend/app/api/models.py to ensure canonical naming conventions
- [ ] Update Creation Station frontend to use consistent names matching database schema
- [ ] Ensure naming consistency flows from database → backend models → API endpoints → frontend
- [ ] Review and update:
  - Database: Check if using "rooms" vs "classrooms" vs "class_chat"
  - Backend models: Align model names with database tables
  - API endpoints: Ensure endpoint naming matches models
  - Frontend: Update all references to match backend naming

## Authentication Roadmap

- [ ] Document tonight's manual onboarding flow (pre-create `user_profile` / `user_auth` rows, hash passwords, share credentials securely) so demos stay self-contained.
- [ ] Weekend: add `/api/v1/auth/signup` gated by invite codes and issue JWT access + refresh tokens (decide HS256 vs RS256, wire env secrets, build rotation + revocation table).
- [ ] Weekend: embed tenant/org/scope claims into tokens and update FastAPI dependencies to enforce multi-tenant access rules.
- [ ] Weekend: enable Postgres RLS or equivalent policy checks for `created_tool`, `created_model`, `resource_shares`, etc., driven by the tenant claims so shared content stays partitioned across schools.
- [ ] Weekend: update frontend auth layer to handle token refresh, logout, and to surface org-aware sharing controls for teachers.
- [x] Weekend: add per-user `session_nonce` storage + validation so admins can revoke sessions instantly across devices.
- [x] Weekend: introduce CSRF protection (double-submit token or same-site POST guard) for any state-changing requests that rely on session cookies.
- [ ] If offline, download `email-validator` wheel separately and install with `pip install --no-index --find-links /path/to/wheels email-validator` before starting Uvicorn.
