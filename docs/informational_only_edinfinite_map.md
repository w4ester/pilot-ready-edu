Edinfinite
“Informational only; not a canonical source” note.


Your fast lane for wiring the demo UI into the stabilized backend. Everything below is live on the `feature/backend-stabilization` branch and verified by the smoke suite.

## 1. Local Environment Cheatsheet

- **Prereqs**: Docker Desktop, Node 20+, pnpm or npm, Python 3.11 (only if you want scripts outside Docker).
- **Project env**: copy `.env.example` → `.env`, ensure
  - `FASTAPI_URL=http://localhost:8000`
  - `DEV_USER_ID=99999999-9999-9999-9999-999999999999`
- **Bring up services**:
  ```bash
  docker compose up -d db redis ollama api
  docker compose run --rm migrate
  cat db/dev_seed_creationstation.sql | docker compose exec -T db psql -U app -d appdb
  ```
- **Smoke sanity** (run after any backend change):
  ```bash
  curl -s http://localhost:8000/health/schema
  curl -s -H 'X-Dev-User-Id:99999999-9999-9999-9999-999999999999' http://localhost:8000/api/v1/tools
  ```

## 2. Seed Data Snapshot

Seeding creates one teacher user (`DEV_USER_ID` above), demo tools/models/libraries, and a class room:

| Record | ID | Notes |
| --- | --- | --- |
| Class Room | `66666666-6666-6666-6666-666666666666` | Default “General” room |
| Library | `11111111-1111-1111-1111-111111111111` | “Sample Library” used in demos |
| Tool | `22222222-2222-2222-2222-222222222222` | `summarize_tool` |
| Model | `44444444-4444-4444-4444-444444444444` | `ELA-Planner` |

Use these IDs directly for quick UI mocks (messages, library listings, etc.).

## 3. API Surface (Frontend-Facing)

All routes expect `X-Dev-User-Id` during dev, unless noted. JSON responses are Pydantic objects defined in `backend/app/api/*.py`.

### 3.1 Tools (`backend/app/api/tools.py`)

| Method & Route | Purpose | Request body | Response |
| --- | --- | --- | --- |
| `GET /api/v1/tools` | List tools for current user | – | `[ToolOut]` (id, slug, language, content, etc.) |
| `POST /api/v1/tools` | Create new tool | `ToolBase` (slug, name, content, optional valves/meta) | `ToolOut` |
| `POST /api/v1/tools/{tool_id}/versions` | Publish new version | `PublishIn` (content/requirements/meta) | `{tool_id, version}` |
| `POST /api/v1/tools/test-run` | Stubbed sandbox preview | `TestRunIn` (code + optional input) | `{ok, message}` |

### 3.2 Models (`backend/app/api/models.py`)

| Method | Route | Notes |
| --- | --- | --- |
| `GET` | `/api/v1/models` | List models for user; attaches seeds (ELA Planner). |
| `POST` | `/api/v1/models` | Create model (`ModelIn`). |
| `POST` | `/api/v1/models/{model_id}/tools` | Attach tools (`AttachPayload.tool_ids`). |
| `POST` | `/api/v1/models/{model_id}/libraries` | Attach libraries (`AttachPayload.library_ids`). |
| `POST` | `/api/v1/models/{model_id}/export/ollama` | Returns simple Modelfile text. |

### 3.3 Prompts (`backend/app/api/prompts.py`)

| Method | Route | Comments |
| --- | --- | --- |
| `GET` | `/api/v1/prompts` | List prompts with variables metadata. |
| `POST` | `/api/v1/prompts/test` | Render prompt with `{"content":"Hello {name}!","variables":{"name":"world"}}` → `{ok, rendered}`. |

### 3.4 Libraries (`backend/app/api/libraries.py`)

| Method | Route | Notes |
| --- | --- | --- |
| `GET` | `/api/v1/libraries` | List accessible libraries. |
| `POST` | `/api/v1/libraries` | Create new library (`{name, description}`) |

### 3.5 Rooms & Messaging (`backend/app/api/rooms.py`)

| Method | Route | Description |
| --- | --- | --- |
| `GET` | `/api/v1/rooms/{room_id}/messages` | Fetch latest messages (default limit 50). |
| `POST` | `/api/v1/rooms/{room_id}/messages` | Send message (`MessageIn`). |
| `POST` | `/api/v1/class_rooms/{room_id}/assistant` | Upsert assistant (stub response). |
| `POST` | `/api/v1/class_rooms/{room_id}/knowledge` | Attach libraries to room. |

## 4. Backend Data Model (ORM highlights)

All SQLAlchemy models live in `backend/app/db/models.py`. Key groups:

- **User-centric**: `user_auth`, `user_settings`, `user_identity`, `user_tag` (id + user composite key).
- **Artifacts & Sharing**: `user_artifact`, `resource_shares`, `user_feedback`, `user_memory`, `app_config`.
- **BYOM Registry**: `model_provider`, `base_model`, `provider_credential`.
- **MCP (Model Context Protocol)**: `mcp_server`, `mcp_server_tool`, `model_mcp_tool`, `mcp_server_version`, `mcp_server_binding`.
- **Platform capabilities**: `platform_capability`, `platform_capability_scope`, `model_capability`, `platform_feature_flag`.
- **Chat hierarchy**: `user_group`, `user_group_member`, `user_folder`, `user_chat`, `user_chat_tag`.

Everything is schema-first: column definitions and indexes match `db/database_schema_consolidated.sql` exactly. No surprise migrations.

## 5. Verification Scripts

- Coverage map: `python scripts/list_schema_mapping.py` (Markdown + CSV).
- Schema smoke: `./scripts/smoke.sh` (wraps all curl checks).

Use these to ensure new UI calls align with the existing APIs.

## 6. Frontend Workflow Tips

- Run `npm install` (or pnpm) inside `/web`, then `npm run dev -- --host --port 5173`.
- Wire API modules via `web/src/lib/api.creationstation.ts` (already references the endpoints above).
- Stick to the seeded IDs while building; the backend enforces ownership and UUIDs.
- Before PRs, re-run the smoke suite and regenerate `docs/schema/orm_coverage.*` if models shift.

Happy wiring—ping if you need request/response samples or mock data tweaks. Let’s GrOw!
