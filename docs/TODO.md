# TODO – Authentication Roadmap

- [ ] Document tonight's manual onboarding flow (pre-create `user_profile` / `user_auth` rows, hash passwords, share credentials securely) so demos stay self-contained.
- [ ] Weekend: add `/api/v1/auth/signup` gated by invite codes and issue JWT access + refresh tokens (decide HS256 vs RS256, wire env secrets, build rotation + revocation table).
- [ ] Weekend: embed tenant/org/scope claims into tokens and update FastAPI dependencies to enforce multi-tenant access rules.
- [ ] Weekend: enable Postgres RLS or equivalent policy checks for `created_tool`, `created_model`, `resource_shares`, etc., driven by the tenant claims so shared content stays partitioned across schools.
- [ ] Weekend: update frontend auth layer to handle token refresh, logout, and to surface org-aware sharing controls for teachers.
