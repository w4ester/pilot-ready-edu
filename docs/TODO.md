Canonical Sources

db/database_schema_consolidated.sql remains the ground truth—docs/review_database_.md already walks you through verifying it in a live DB (\dt, \d+, the information_schema queries). Keep using that flow whenever you need to confirm actual columns or defaults.
docs/schema/database_schema_map.json is a comprehensive catalog that restates every column/constraint in plain English. It mirrors the SQL schema; as long as you regenerate or edit it whenever the DDL changes, it’s a perfect “human contract” to reference from docs or the upcoming API contract file.
docs/schema/orm_coverage.md shows a one-to-one checklist between tables and SQLAlchemy models, confirming the ORM layer still reflects the canonical table names—no drift today.
Next Actions

Treat the SQL file as the single source, and update database_schema_map.json via the existing scripts (scripts/list_schema_mapping.py) whenever the schema changes so documentation stays in sync.
When you create docs/api_contract/login.yaml, pull the field names directly from the SQL/JSON map to ensure the contract is anchored to those canonical spellings.
Add a note to docs/review_database_.md (or an ADR) pointing readers to database_schema_map.json and the SQL script so future developers or LLMs know exactly where the truth lives and how to verify it.