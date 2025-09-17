Demo-Ready Checklist (End-to-end)

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
7. Final Demo Prep

Ensure docker compose up -d api before demo (backend hot-reloads).
Use docker compose logs -f api to watch for issues.
Optional: export Postgres snapshot (docker compose exec db pg_dump … > demo_snapshot.sql).
Once these steps are green, the backend, database, and front-end wiring are ready to showcase.
