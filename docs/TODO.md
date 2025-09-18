Demo-Ready Checklist (End-to-end)

Smoke Test Follow-ups (2025-09-17)

- API container logs show `pydantic.errors.PydanticImportError` complaining that `BaseSettings` moved to `pydantic-settings`. Per Pydantic v2 docs, `BaseSettings` now lives in the separate `pydantic-settings` package and apps should `pip install pydantic-settings` and import with `from pydantic_settings import BaseSettings`. The runtime image likely predates that package in `requirements.txt`, so we need a `docker compose build --no-cache api` (and worker) once to bake the new dependency.
- `/api/v1/tools` returns 500 because the `db` dependency provides a `_GeneratorContextManager`. In FastAPI the recommended Pydantic 2 style is to define the dependency as a plain generator (`def get_db(): db = SessionLocal(); try: yield db; finally: db.close()`); decorating it with `@contextmanager` causes FastAPI to inject the context manager object, which fails when we call `.query(...)`.
- Pydantic 2 introduces protected namespaces (`model_`, `serializer_`, `__`) defined via `model_config = ConfigDict(protected_namespaces=('model_', 'serializer_', ...))`. Our schemas with `model_id` now hit that guard, so either disable it (`model_config = ConfigDict(protected_namespaces=())`) or rename the field (e.g. `assistant_model_id`). Decide which approach keeps API contracts stable before touching code.

Embedding Alignment (2025-09-18)

- Measured `gemma:2b-embeddings` output (768-dim). Applied Alembic revision `0003_align_embedding_dimension.py` to convert `document_chunk.embedding` to `vector(768)` and recreate the `idx_document_chunk_embedding_hnsw` cosine index.
- Rebuilt `api` image and reran smoke: `GET /health/schema` (2025-09-18T01:49:50Z) → 200; `GET /api/v1/tools` with dev header → 200 returning seeded `summarize_tool`. API logs remained clean.
- Next backend focus: clear the remaining `[ ]` tables from `scripts/list_schema_mapping.py` (starting with user_auth/settings/identity, organization*, library_document/document_chunk, and MCP/platform capability tables).

Pending Fix Plan (awaiting green light)

Blockers (fix first)

1. `backend/app/db/session.py` — FastAPI `yield` dependency merged. ✔
2. `backend/app/api` schemas with `model_id` fields — now inherit from `ApiBaseModel`; warning resolved. ✔
3. Router/legacy cleanup — removed `backend/app/routers/health.py` and `backend/app/db/tools.py`. ✔
4. Backend image refresh — rebuilt `api` service after ORM UUID alignment. ✔
5. Smoke verification — health, tools, models, prompts/test, libraries (list/create), room messages (GET/POST), assistant upsert, and knowledge attach all return expected 200/201 responses. ✔

Verification Checklist

- `GET /health/schema` → 200
- `GET /api/v1/tools` with `X-Dev-User-Id` → 200
- Log tail free of `pydantic` protected-namespace warnings
- `document_chunk.embedding` → `vector(768)` with `idx_document_chunk_embedding_hnsw` rebuilt

Next Steps (post-fix)

- Finish prompts/models UI wiring (per broader TODO)
- Add auth endpoints (/auth/register, /auth/login, /auth/accept-invite)
- Ensure classroom creation seeds default assistant and room
- Stashed WIP (`stash@{0}`) for API/seed/frontend edits — restore with `git stash pop` when ready; use `git stash apply` to preview, `git stash drop` to remove.

1. Start Clean

git pull latest changes; confirm git status -s is clean.
docker compose pull db redis ollama
docker compose up -d db redis ollama
Verify docker compose ps → Postgres healthy, Redis/Ollama running.
2. Migrate & Seed

Run docker compose run --rm migrate (Alembic applies baseline + 0002_vector_768_hnsw).
Seed demo teacher/class/tool/model:
cat db/dev_seed_creationstation.sql | \
  docker compose exec -T db psql -U app -d appdb
Sanity query: docker compose exec db psql -U app -d appdb -c "SELECT id,name FROM created_model;".
3. Backend Coverage

Creation Station: /api/v1/tools and /api/v1/models already live (FastAPI modules in backend/app/api/).
Add missing routers before demo:
Prompts — DONE
ORM: add CreatedPrompt to backend/app/db/models.py. — DONE
API: create backend/app/api/prompts.py with list/create/update/test endpoints. — DONE
Include router in backend/app/api/__init__.py. — DONE
Libraries — DONE
ORM: ensure Library, LibraryDocument, DocumentChunk already present (done); expose APIs for list/add. — DONE (list/add)
Rooms & Messaging — DONE
ORM: add classes for class_room, class_room_member, class_message, class_message_reaction, class_read_receipt, class_assistant, class_knowledge. — DONE
API module (e.g. backend/app/api/rooms.py) with:
GET/POST /rooms/{roomId}/messages — DONE
GET/POST /class_rooms/{roomId}/assistant — DONE (stubbed reply)
POST /class_rooms/{roomId}/knowledge — DONE
Provide stubbed assistant reply (log request or return placeholder). — DONE
Run docker compose run --rm migrate for any new migrations created during API work.
4. Manual Endpoint Checks

Health: curl -sf http://localhost:8000/health/schema
Tools: curl -sf http://localhost:8000/api/v1/tools -H "X-Dev-User-Id: <DEV_USER_ID>"
Models, Prompts, Libraries similar.
Messages: create/list via curl to confirm ORM/API flow is good.
5. Update Docs & TODO

Mark completed items in docs/TODO.md.
Record API additions in docs/schema/CHANGELOG.md.
Run git status -s → ensure only intended files changed, commit.
6. Frontend Handoff

Ensure .env contains:
FASTAPI_URL=http://localhost:8000
DEV_USER_ID=99999999-9999-9999-9999-999999999999
cd web && npm install (once).
npm run dev -- --host --port 5173.
Wire UI screens to call:
/api/v1/tools (list/create).
/api/v1/models (list/attach/export).
/api/v1/prompts, /api/v1/libraries.
Messaging endpoints for demo room.
Verify seeded teacher and sample tool appear in UI.

Note: Share frontend screenshots and simple HTML snippets with the team before converting them into native frontend code tomorrow.
7. Final Demo Prep

Ensure docker compose up -d api before demo (backend hot-reloads).
Use docker compose logs -f api to watch for issues.
Optional: export Postgres snapshot (docker compose exec db pg_dump … > demo_snapshot.sql).
Once these steps are green, the backend, database, and front-end wiring are ready to showcase.
