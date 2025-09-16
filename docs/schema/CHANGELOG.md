# Schema Changelog

## 2025-09-16
- Added baseline consolidated schema `database_schema_consolidated.sql`.
- Added MCP tables, platform capability tables, and supporting index patch scripts.
- Added backend requirements scaffold (`backend/requirements.txt`) and FastAPI skeleton (health routes, settings).
- Added Docker Compose stack, environment template, database init SQL enabling pgcrypto/citext/vector, and backend Dockerfile.
- Added SvelteKit starter (monaco-enabled landing page) and web Docker ignore.
- Updated schema map check script to target `docs/schema/database_schema_map.json`.
