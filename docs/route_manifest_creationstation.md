# Creation Station Route Manifest

## Frontend (SvelteKit)

| Route | Component Path | Purpose | Status |
| --- | --- | --- | --- |
| `/creationstation` | `web/src/routes/creationstation/+page.svelte` | Teacher hub with feature cards | Implemented |
| `/creationstation/studio` | `web/src/routes/creationstation/studio/+page.svelte` | Links to Prompts, Tools, Models | Implemented |
| `/prompts` | `web/src/routes/prompts/+page.svelte` | Prompt Library (list/create/edit/test) | Planned |
| `/prompts/new` | `web/src/routes/prompts/new/+page.svelte` | New Prompt editor | Planned |
| `/prompts/[id]` | `web/src/routes/prompts/[id]/+page.svelte` | Edit a Prompt | Planned |
| `/tools` | `web/src/routes/tools/+page.svelte` | Tool Library (list/create/version/test) | Planned |
| `/tools/new` | `web/src/routes/tools/new/+page.svelte` | New Tool (Monaco + AI helper) | Planned |
| `/tools/[id]` | `web/src/routes/tools/[id]/+page.svelte` | Tool detail & versions | Planned |
| `/models` | `web/src/routes/models/+page.svelte` | Model Library (list/create/attach) | Planned |
| `/models/new` | `web/src/routes/models/new/+page.svelte` | Model Builder | Planned |
| `/models/[id]` | `web/src/routes/models/[id]/+page.svelte` | Model detail & export | Planned |
| `/classes` | `web/src/routes/classes/+page.svelte` | Class list & CTA "New Class" | Implemented (placeholder) |
| `/classes/[id]` | `web/src/routes/classes/[id]/+page.svelte` | Class overview (rooms, invite) | Planned |
| `/classes/[id]/rooms/[roomId]` | `web/src/routes/classes/[id]/rooms/[roomId]/+page.svelte` | Class room chat | Planned |
| `/lesson-planner` | `web/src/routes/lesson-planner/+page.svelte` | Instant lesson planning | Planned |
| `/assessments` | `web/src/routes/assessments/+page.svelte` | Assessment Studio | Planned |
| `/join` | `web/src/routes/join/+page.svelte` | Teacher registration (allow-list/invite) | Planned |

## Backend API (FastAPI `/api/v1/*`)

### Auth
- `POST /auth/register` — create `user_auth` + `user_profile` (teacher); allow-list or invite. *(Implemented)*
- `POST /auth/login` — issue session JWT. *(Implemented)*
- `GET /auth/accept-invite` — validate teacher invite token. *(Implemented)*

### Classes & Rooms
- `GET /classes` — list classes for current user. *(Planned)*
- `POST /classes` — create class, add teacher, bootstrap "general" room + assistant. *(Implemented)*
- `GET /classes/{id}` — class detail (rooms, members, assistant). *(Planned)*
- `POST /classes/invite` — issue `class_join` token for students. *(Implemented)*
- `POST /classes/join` — consume join token. *(Implemented)*
- `POST /classes/{id}/rooms` — create additional room. *(Planned)*

### Room Messages & Config
- `GET /rooms/{roomId}/messages` — list messages. *(Planned)*
- `POST /rooms/{roomId}/messages` — post message; assistant replies. *(Planned)*
- `GET /rooms/{roomId}/assistant` — fetch assistant config. *(Planned)*
- `POST /rooms/{roomId}/assistant` — update assistant (model, tools, prompt). *(Planned)*
- `POST /rooms/{roomId}/knowledge` — attach/detach libraries. *(Planned)*

### Prompts
- CRUD under `/prompts` + `/prompts/test`. *(Planned)*

### Tools
- CRUD under `/tools`, publish versions, `/tools/test-run`. *(Planned)*

### Models
- CRUD under `/models`, attach tools/libraries, `/models/{id}/export/ollama`. *(Planned)*

### Libraries
- CRUD under `/libraries`, ingest documents, chunk/embedding pipeline. *(Planned)*

### Health
- `GET /health/schema` — returns Alembic head revision. *(Implemented)*

## Backend File Map
- `backend/app/api/auths.py` — register/login/accept-invite
- `backend/app/api/classes.py` — class management + join tokens
- `backend/app/api/prompts.py` — prompts CRUD/test *(planned)*
- `backend/app/api/tools.py` — tools CRUD/version/test *(planned)*
- `backend/app/api/models.py` — models CRUD/attach/export *(planned)*
- `backend/app/api/rooms.py` — messages, assistant, knowledge *(planned)*

## DB Touchpoints
- Auth → `user_auth`, `user_profile`, `organization_domain`
- Classes → `user_group`, `user_group_member`, `group_chat_channel`, `channel_assistant`, `channel_knowledge`
- Prompts → `created_prompt`
- Tools → `created_tool`, `created_tool_version`, `model_tool`
- Models → `created_model`, `model_tool`, `model_library`, `base_model`
- Libraries → `library`, `library_document`, `document_chunk`, `library_file`
- Messages → `channel_message`, `channel_message_reaction`, `channel_read_receipt`

## Anti-Drift Rules
1. Teacher hub paths live under `/creationstation` (never `/dashboard`).
2. Creation Station feature pages reside under `/prompts`, `/tools`, `/models`.
3. Room configuration routes are namespaced by room ID.
4. Any route change must update this manifest **and** `routes.openapi.yaml`; CI should diff OpenAPI to block drift.
