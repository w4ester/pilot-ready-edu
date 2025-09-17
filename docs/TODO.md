Edinfinite Build Backlog (schema-aligned)
Authentication & Account Flow
 Implement POST /api/v1/auth/register with organization allow‑list + invite token validation (touches user_auth, user_profile, organization_domain, organization_idp).
 Implement POST /api/v1/auth/login returning a session JWT; persist hashed passwords in user_auth.password.
 Implement GET /api/v1/auth/accept-invite to validate teacher invites.
 Seed default user_settings row for each new teacher (table: user_settings).
Teacher Onboarding & Classes
 POST /api/v1/classes: create user_group (class), default class_room, and seed class_assistant.
 GET /api/v1/classes: list classes using user_group + user_group_member.
 Support student join tokens (POST /api/v1/classes/invite, POST /api/v1/classes/join) backed by resource_shares.
 Seed demo teacher + class + room (db/dev_seed_creationstation.sql).
Creation Station (Prompts / Tools / Models)
 Align ORM models with canonical tables: created_tool, created_tool_version, created_model, model_tool, model_library, created_prompt.
 Finish /api/v1/tools (CRUD/version/test-run) using those ORM models.
 Finish /api/v1/models (CRUD + attach tools/libraries + export).
 Add routers for prompts and libraries per route manifest.
Rooms & Messaging
 Build message APIs on top of class_room, class_room_member, class_message, class_message_reaction, class_read_receipt:
GET /rooms/{roomId}/messages
POST /rooms/{roomId}/messages
Provide an assistant-response stub wired to class_assistant
 Assistant configuration endpoints using class_assistant + class_knowledge:
GET /class_rooms/{roomId}/assistant
POST /class_rooms/{roomId}/assistant
POST /class_rooms/{roomId}/knowledge
Frontend Tasks
 Scaffold Creation Station routes (/prompts, /tools, /models) per docs/route_manifest_creationstation.md.
 Implement join/register UI with domain allow-list + invite flow.
 Hook Monaco artifact sandbox into tool/model editors.
Infrastructure
 Maintain Alembic migrations matching db/database_schema_consolidated.sql (baseline 0001, revision 0002_vector_768_hnsw in backend/alembic/versions/).
 Add CI guard to ensure docs/TODO.md changes are intentional.