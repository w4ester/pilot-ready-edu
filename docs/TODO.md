# Edinfinite Build Backlog

## Authentication & Account Flow
- [ ] Implement `/api/v1/auth/register` with organization allow-list + invite token support.
- [ ] Implement `/api/v1/auth/login` returning session JWT.
- [ ] Implement `/api/v1/auth/accept-invite` to validate teacher invites.
- [ ] Persist and hash passwords in `user_auth` (argon2/bcrypt) and set default `user_settings` rows.

## Teacher Onboarding & Classes
- [ ] Create class bootstrap endpoint (`POST /api/v1/classes`) to add teacher, create default room, and bind assistant.
- [ ] Implement class listing (`GET /api/v1/classes`) for current user.
- [ ] Support student join tokens (`POST /api/v1/classes/invite` + `/api/v1/classes/join`).
- [ ] Seed initial teacher + class + room for demo (`db/dev_seed_creationstation.sql`).

## Creation Station (Prompts / Tools / Models)
- [ ] Align ORM models with canonical schema (include slug, language, user_id, etc.).
- [ ] Wire `/api/v1/tools` router into FastAPI and finish CRUD/version/test run.
- [ ] Wire `/api/v1/models` router and attach/export endpoints.
- [ ] Add prompts and libraries routers to match manifest.

## Rooms & Messaging
- [ ] Implement room message listing/posting + assistant response stub.
- [ ] Add assistant configuration endpoints (`/rooms/{roomId}/assistant`, `/knowledge`).

## Frontend Tasks
- [ ] Scaffold Creation Station child routes (`/prompts`, `/tools`, `/models` etc.) per manifest.
- [ ] Implement join/register UI with domain allow-list + invite link support.
- [ ] Hook Monaco artifact sandbox into tool/model editors.

## Infrastructure
- [ ] Add Alembic migrations for canonical DDL + new API tables.
- [ ] Add CI check to diff `docs/TODO.md` when tasks change.
