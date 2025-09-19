Canonical Sources

<docs/schema/database_schema_map.json> is the canonical catalog. Every table entry has the real table_name, plus all columns, constraints, and descriptions. Whenever we change the schema, regenerate this file (see next point) and both the backend and frontend can read from the same source.

<Quick extract of just the table names:>
jq -r '.tables[].table_name' docs/schema/database_schema_map.json
Columns for one table:
jq '.tables[] | select(.table_name=="created_tool").columns' docs/schema/database_schema_map.json
scripts/list_schema_mapping.py cross-checks the SQL snapshot (db/database_schema_consolidated.sql) against the ORM. Run it before wiring to make sure nothing drifted:

<python scripts/list_schema_mapping.py --format markdown >
That gives you a checklist of table_name → ORM class; you can keep the file open while you work on the front end.

If you ever worry the JSON is stale, regenerate it from the SQL snapshot using your existing tooling (scripts/check_schema_map_ids.py or whatever command you normally use when updating the schema docs). With that pipeline, you and I can both rely on the same canonical names while wiring the frontend, and you’re guaranteed we’re matching the real Postgres schema

<db/database_schema_consolidated.sql remains the ground truth—docs/review_database_.md >
already walks you through verifying it in a live DB (\dt, \d+, the information_schema queries). Keep using that flow whenever you need to confirm actual columns or defaults.
<docs/schema/database_schema_map.json> is a comprehensive catalog that restates every column/constraint in plain English. It mirrors the SQL schema; as long as you regenerate or edit it whenever the DDL changes, it’s a perfect “human contract” to reference from docs or the upcoming API contract file.

<docs/schema/orm_coverage.md> shows a one-to-one checklist between tables and SQLAlchemy models, confirming the ORM layer still reflects the canonical table names—no drift today.


Treat the SQL file as the single source, and update database_schema_map.json via the existing scripts (scripts/list_schema_mapping.py) whenever the schema changes so documentation stays in sync.

Add a note to docs/review_database_.md (or an ADR) pointing readers to database_schema_map.json and the SQL script so future developers or LLMs know exactly where the truth lives and how to verify it.


## Backend and FrontEnd
backend and frontend aligned to the real database names is safest approach for naming and no drift.

## Backend: 
SQLAlchemy models mirror the canonical table names (see <orm_coverage.md>), and as long as keep adding columns/relationships to those models instead of inventing aliases, the API stays grounded in the schema. 

## Important 
Whenever the DB changes, re-run scripts/list_schema_mapping.py or check_schema_map.py so the generated map keeps tracking the exact column names/types.

## Frontend: 
Pull the field names straight from the API responses, which in turn come from those same ORM models. This means no drift renaming things in the UI layer, and avoids mismatches when the schema evolves. If the API schema ever adds a new column like created_at, it flows through without translation work.

## Documentation: 
Treat db/database_schema_consolidated.sql as the single source. When it changes, regenerate docs/schema/database_schema_map.json and update the walkthrough docs. review_database_.md and information_schema_read.md will stay accurate if they simply reference that map.

Use the canonical names everywhere is the quickest way to stay in sync with the real schema while we wire up the demo branch.


## DB Canonical Names:
user_auth
user_profile
user_settings
user_group
user_group_member
class_room
class_room_member
class_read_receipt
user_chat
user_chat_tag
app_config
user_feedback
user_file
user_folder
library
user_memory
class_message
class_message_reaction
created_model
created_prompt
user_tag
created_tool
created_tool_version
model_tool
model_library
user_identity
organization
organization_domain
organization_idp
user_artifact
resource_shares
class_assistant
class_knowledge
library_document
document_chunk
library_file
model_provider
base_model
provider_credential
group_artifact_access (VIEW)
user_function (DEPRECATED)
mcp_server
mcp_server_tool
model_mcp_tool
mcp_server_version
mcp_server_binding
platform_capability
platform_capability_scope
model_capability
platform_feature_flag

## Canonical DB matches for backend are foud in backend/app/db/models.py
Backend naming find mapping report for every table in db/database_schema_consolidated.sql has a matching SQLAlchemy model using the same canonical name (created_tool ↔ CreatedTool, class_room ↔ ClassRoom, etc.), and there are no stray ORM models pointing at non-existent tables. In short, the backend is already aligned with the database vocabulary, so we can wire the frontend against these names confidently once we knock out the access-control fixes.


To see a full crosswalk straight from scripts/list_schema_mapping.py, so you can see every canonical table in the SQL snapshot and the ORM class that maps to it inside backend/app/db/models.py: run scripts/list_schema_mapping.py. to then see output at/pilot-ready-edu/docs/schema_map.csv'

Front end names have to be 
Use the exact resource and field names exposed by the API—which mirror the canonical tables. For example, when you render or bind data in Svelte, expect JSON objects shaped like the ORM models: created_tool records (with properties such as id, user_id, slug, name, language, entrypoint, content, …), created_model, model_tool, created_prompt, class_room, and so on. The CSV we generated (docs/schema_map.csv) is your quick reference for the canonical plural name (created_tool) and the corresponding server-side model (CreatedTool). As long as the frontend sticks to those names, you’re speaking the same language as the database and the backend contracts.
also quick reference is pilot-ready-edu/docs/schema_map.csv