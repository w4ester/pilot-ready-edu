# Schema Changelog

## 2025-09-17
- `document_chunk.embedding` now uses `vector(768)`.
- ANN index switched from IVFFlat to HNSW (cosine) as `idx_document_chunk_embedding_hnsw`.
- GIN index on `content_tsv` retained.

## 2025-09-16
- Added baseline consolidated schema `database_schema_consolidated.sql`.
- Added MCP tables, platform capability tables, and supporting index patch scripts.
- Added backend requirements scaffold (`backend/requirements.txt`) and FastAPI skeleton (health routes, settings).
- Added Docker Compose stack, environment template, database init SQL enabling pgcrypto/citext/vector, and backend Dockerfile.
- Added SvelteKit starter with Monaco-based artifact sandbox and web Docker ignore.
- Updated schema map check script to target `docs/schema/database_schema_map.json`.
- Rebranded project assets to “Edinfinite” (docs, compose header, Monaco UI).
- Expanded backend requirements to document optional integrations (auth, BYOM providers, RAG toolchain, observability).
- Added stack versions summary (`docs/stack_versions.md`) and Creation Station route manifest (`docs/route_manifest_creationstation.md`, `docs/routes.openapi.yaml`).
