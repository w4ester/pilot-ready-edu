
Step 1: Copy the baseline environment file

cp .env.example .env — makes your personal .env by duplicating the sample. This keeps the real connection credentials out of Git while matching what the stack expects.
Step 2: Start only the database service

docker compose up -d db — launches the Postgres container in the background (-d) without touching other services, so we have a running database to inspect.
Step 3: Open a psql session inside the container

docker compose exec db psql -U ${POSTGRES_USER:-app} -d ${POSTGRES_DB:-appdb} — jumps into the db container and starts psql. The -U flag supplies the username (default app), and -d selects the database (default appdb), both matching .env.
Step 4: Confirm schemas exist

\dn — psql meta-command that lists schemas; confirms public (and any others) are present before we drill into tables.
Step 5: List every table in the public schema

\dt public.* — shows all relations classified as tables under public, giving you table names and owners so you know what objects you’re about to inspect.
Step 6: Review indexes globally

\di+ — lists indexes across the current database with extra info (+), helping you see existing performance/configuration structures without altering anything.
Step 7: Inspect a specific table’s structure

\d+ public.table_name — replace table_name with each table of interest. This reveals columns, data types, defaults, constraints, and attached indexes all in one view.
Step 8: Pull a complete column catalog

SELECT table_name, ordinal_position, column_name,
       data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;
— standard SQL query against information_schema. It compiles every column’s metadata across public, sorted by table and column order, giving a matrix you can export.
Step 9: Identify primary keys

SELECT tc.table_name, kcu.column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
  ON tc.constraint_name = kcu.constraint_name
 AND tc.table_schema = kcu.table_schema
WHERE tc.constraint_type = 'PRIMARY KEY'
  AND tc.table_schema = 'public'
ORDER BY tc.table_name, kcu.ordinal_position;
— joins the constraint views so you know which columns form each primary key, ordered as defined.
Step 10: Map foreign-key relationships

SELECT tc.table_name AS source_table,
       kcu.column_name AS source_column,
       ccu.table_name AS target_table,
       ccu.column_name AS target_column,
       tc.constraint_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
  ON tc.constraint_name = kcu.constraint_name
 AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage ccu
  ON ccu.constraint_name = tc.constraint_name
 AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'public'
ORDER BY source_table, tc.constraint_name, kcu.ordinal_position;
— cross-references source and target tables/columns to give the relationship map, so you can trace how records link.
Step 11: Capture the entire schema snapshot (optional read-only export)

docker compose exec db pg_dump --schema-only --no-owner --no-privileges -U app appdb > schema_snapshot.sql — runs pg_dump inside the container but outputs only DDL (no data). Redirects it to schema_snapshot.sql on your host so you have a full-text schema archive without mutating the database.
Let me know if you want to dig into any particular table or run these interactively together.



\dn — confirms available schemas (you should see public).
\dt public.* — lists every table in the public schema so you know what exists.
\di+ — shows all indexes with details.



\dt public.*
List of relations

Schema |           Name            | Type  | Owner 
--------+---------------------------+-------+-------
 public | alembic_version           | table | app
 public | app_config                | table | app
 public | base_model                | table | app
 public | class_assistant           | table | app
 public | class_knowledge           | table | app
 public | class_message             | table | app
 public | class_message_reaction    | table | app
 public | class_read_receipt        | table | app
 public | class_room                | table | app
 public | class_room_member         | table | app
 public | created_model             | table | app
 public | created_prompt            | table | app
 public | created_tool              | table | app
 public | created_tool_version      | table | app
 public | document_chunk            | table | app
 public | library                   | table | app
 public | library_document          | table | app
 public | library_file              | table | app
 public | mcp_server                | table | app
 public | mcp_server_binding        | table | app
 public | mcp_server_tool           | table | app
 public | mcp_server_version        | table | app
 public | model_capability          | table | app
 public | model_library             | table | app
 public | model_mcp_tool            | table | app
 public | model_provider            | table | app
 public | model_tool                | table | app
 public | organization              | table | app
 public | organization_domain       | table | app
 public | organization_idp          | table | app
 public | platform_capability       | table | app
 public | platform_capability_scope | table | app
 public | platform_feature_flag     | table | app
 public | provider_credential       | table | app
 public | resource_shares           | table | app
 public | user_artifact             | table | app
 public | user_auth                 | table | app
 public | user_chat                 | table | app
 public | user_chat_tag             | table | app
 public | user_feedback             | table | app
 public | user_file                 | table | app
 public | user_folder               | table | app
 public | user_group                | table | app
 public | user_group_member         | table | app
 public | user_identity             | table | app
 public | user_memory               | table | app
 public | user_profile              | table | app
 public | user_settings             | table | app
 public | user_tag                  | table | app
(49 rows)
(END)


\di+ to review all indexes the schema already has.

\di+
Schema |                        Name                        | Type  | Owner |           Table           | Persistence | Access method |    Size    | Description 
--------+----------------------------------------------------+-------+-------+---------------------------+-------------+---------------+------------+-------------
 public | alembic_version_pkc                                | index | app   | alembic_version           | permanent   | btree         | 16 kB      | 
 public | app_config_pkey                                    | index | app   | app_config                | permanent   | btree         | 8192 bytes | 
 public | base_model_pkey                                    | index | app   | base_model                | permanent   | btree         | 8192 bytes | 
 public | class_assistant_pkey                               | index | app   | class_assistant           | permanent   | btree         | 16 kB      | 
 public | class_knowledge_pkey                               | index | app   | class_knowledge           | permanent   | btree         | 16 kB      | 
 public | class_message_pkey                                 | index | app   | class_message             | permanent   | btree         | 16 kB      | 
 public | class_message_reaction_message_id_user_id_name_key | index | app   | class_message_reaction    | permanent   | btree         | 8192 bytes | 
 public | class_message_reaction_pkey                        | index | app   | class_message_reaction    | permanent   | btree         | 8192 bytes | 
 public | class_read_receipt_pkey                            | index | app   | class_read_receipt        | permanent   | btree         | 8192 bytes | 
 public | class_room_member_pkey                             | index | app   | class_room_member         | permanent   | btree         | 8192 bytes | 
 public | class_room_pkey                                    | index | app   | class_room                | permanent   | btree         | 16 kB      | 
 public | created_model_pkey                                 | index | app   | created_model             | permanent   | btree         | 16 kB      | 
 public | created_prompt_pkey                                | index | app   | created_prompt            | permanent   | btree         | 8192 bytes | 
 public | created_tool_pkey                                  | index | app   | created_tool              | permanent   | btree         | 16 kB      | 
 public | created_tool_version_pkey                          | index | app   | created_tool_version      | permanent   | btree         | 16 kB      | 
 public | created_tool_version_tool_id_version_key           | index | app   | created_tool_version      | permanent   | btree         | 16 kB      | 
 public | document_chunk_pkey                                | index | app   | document_chunk            | permanent   | btree         | 8192 bytes | 
 public | idx_base_model_provider                            | index | app   | base_model                | permanent   | btree         | 8192 bytes | 
 public | idx_class_assistant_room                           | index | app   | class_assistant           | permanent   | btree         | 16 kB      | 
 public | idx_class_message_parent                           | index | app   | class_message             | permanent   | btree         | 8192 bytes | 
 public | idx_class_message_room                             | index | app   | class_message             | permanent   | btree         | 16 kB      | 
 public | idx_class_message_room_created                     | index | app   | class_message             | permanent   | btree         | 16 kB      | 
 public | idx_class_message_user                             | index | app   | class_message             | permanent   | btree         | 16 kB      | 
 public | idx_class_read_receipt_user                        | index | app   | class_read_receipt        | permanent   | btree         | 8192 bytes | 
 public | idx_class_room_class                               | index | app   | class_room                | permanent   | btree         | 16 kB      | 
 public | idx_created_tool_user                              | index | app   | created_tool              | permanent   | btree         | 16 kB      | 
 public | idx_document_chunk_doc                             | index | app   | document_chunk            | permanent   | btree         | 8192 bytes | 
 public | idx_document_chunk_embedding_hnsw                  | index | app   | document_chunk            | permanent   | hnsw          | 16 kB      | 
 public | idx_document_chunk_tsv_gin                         | index | app   | document_chunk            | permanent   | gin           | 16 kB      | 
 public | idx_document_chunk_unique                          | index | app   | document_chunk            | permanent   | btree         | 8192 bytes | 


 After those listings, pick any table and run \d+ public.table_name to see its columns, types, defaults, constraints, and related indexes. Let me know what output you want to interpret next.

Pick a table and run \d+ public.table_name — replace table_name with one from the list. The output breaks down columns, data types, defaults, constraints, and the indexes tied to that table.
When you’re ready for the full column matrix, paste the information_schema.columns query we prepared:

SELECT table_name, ordinal_position, column_name,
       data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;

Walk Table By Table

Stay at the appdb=# prompt and simply run \d+ public.table_name for each table name from your list. Example: \d+ public.class_room shows every column, type, default, index, and foreign-key on class_room. Repeat with the next table.
Make the walkthrough easier

\pset pager off turns off the pager so long outputs just spill to the screen (no more (END) pauses).
Use tab completion: type \d+ public.cla then press Tab and psql will fill in matching table names.
If you want to capture all table definitions in one sweep, run \pset pager off and then \d+ public.*; psql will dump every table’s structure sequentially so you can scroll or copy it into your doc.



\d+ public.alembic_version
                                               Table "public.alembic_version"
   Column    |         Type          | Collation | Nullable | Default | Storage  | Compression | Stats target | Description 
-------------+-----------------------+-----------+----------+---------+----------+-------------+--------------+-------------
 version_num | character varying(32) |           | not null |         | extended |             |              | 
Indexes:
    "alembic_version_pkc" PRIMARY KEY, btree (version_num)
Access method: heap


\d+ public.app_config
                                          Table "public.app_config"
   Column   |  Type   | Collation | Nullable | Default  | Storage  | Compression | Stats target | Description 
------------+---------+-----------+----------+----------+----------+-------------+--------------+-------------
 id         | integer |           | not null |          | plain    |             |              | 
 data       | jsonb   |           | not null |          | extended |             |              | 
 version    | integer |           | not null |          | plain    |             |              | 
 created_at | bigint  |           | not null | now_ms() | plain    |             |              | 
 updated_at | bigint  |           | not null | now_ms() | plain    |             |              | 
Indexes:
    "app_config_pkey" PRIMARY KEY, btree (id)
Triggers:
    trg_app_config_updated_at BEFORE UPDATE ON app_config FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap



\d+ public.base_model
                                             Table "public.base_model"
    Column     |  Type   | Collation | Nullable |   Default   | Storage  | Compression | Stats target | Description 
---------------+---------+-----------+----------+-------------+----------+-------------+--------------+-------------
 id            | text    |           | not null |             | extended |             |              | 
 provider_id   | uuid    |           | not null |             | plain    |             |              | 
 modality      | text    |           | not null |             | extended |             |              | 
 embedding_dim | integer |           |          |             | plain    |             |              | 
 meta          | jsonb   |           |          | '{}'::jsonb | extended |             |              | 
 created_at    | bigint  |           | not null | now_ms()    | plain    |             |              | 
 updated_at    | bigint  |           | not null | now_ms()    | plain    |             |              | 
Indexes:
    "base_model_pkey" PRIMARY KEY, btree (id)
    "idx_base_model_provider" btree (provider_id)
Foreign-key constraints:
    "base_model_provider_id_fkey" FOREIGN KEY (provider_id) REFERENCES model_provider(id) ON DELETE CASCADE
Triggers:
    trg_base_model_updated_at BEFORE UPDATE ON base_model FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap



\d+ public.class_assistant
                                                Table "public.class_assistant"
       Column       |  Type   | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
--------------------+---------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id                 | uuid    |           | not null | gen_random_uuid() | plain    |             |              | 
 class_room_id      | uuid    |           | not null |                   | plain    |             |              | 
 created_by_user_id | uuid    |           | not null |                   | plain    |             |              | 
 model_id           | text    |           | not null |                   | extended |             |              | 
 name               | text    |           |          |                   | extended |             |              | 
 system_prompt      | text    |           |          |                   | extended |             |              | 
 temperature        | numeric |           | not null | 0.7               | main     |             |              | 
 invocation_mode    | text    |           | not null | 'manual'::text    | extended |             |              | 
 tool_config        | jsonb   |           |          | '{}'::jsonb       | extended |             |              | 
 is_active          | boolean |           | not null | true              | plain    |             |              | 
 created_at         | bigint  |           | not null | now_ms()          | plain    |             |              | 
 updated_at         | bigint  |           | not null | now_ms()          | plain    |             |              | 
Indexes:
    "class_assistant_pkey" PRIMARY KEY, btree (id)
    "idx_class_assistant_room" btree (class_room_id)
Check constraints:
    "class_assistant_invocation_mode_check" CHECK (invocation_mode = ANY (ARRAY['manual'::text, 'on_mention'::text, 'auto'::text]))
    "class_assistant_temperature_check" CHECK (temperature >= 0::numeric AND temperature <= 2::numeric)
Foreign-key constraints:
    "class_assistant_class_room_id_fkey" FOREIGN KEY (class_room_id) REFERENCES class_room(id) ON DELETE CASCADE
    "class_assistant_created_by_user_id_fkey" FOREIGN KEY (created_by_user_id) REFERENCES user_profile(id)
Referenced by:
    TABLE "mcp_server_binding" CONSTRAINT "mcp_server_binding_assistant_id_fkey" FOREIGN KEY (assistant_id) REFERENCES class_assistant(id) ON DELETE CASCADE
    TABLE "platform_capability_scope" CONSTRAINT "platform_capability_scope_assistant_id_fkey" FOREIGN KEY (assistant_id) REFERENCES class_assistant(id) ON DELETE CASCADE
Triggers:
    trg_class_assistant_updated_at BEFORE UPDATE ON class_assistant FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap



\d+ public.class_knowledge
                                           Table "public.class_knowledge"
       Column       |  Type  | Collation | Nullable | Default  | Storage | Compression | Stats target | Description 
--------------------+--------+-----------+----------+----------+---------+-------------+--------------+-------------
 class_room_id      | uuid   |           | not null |          | plain   |             |              | 
 library_id         | uuid   |           | not null |          | plain   |             |              | 
 created_by_user_id | uuid   |           | not null |          | plain   |             |              | 
 created_at         | bigint |           | not null | now_ms() | plain   |             |              | 
Indexes:
    "class_knowledge_pkey" PRIMARY KEY, btree (class_room_id, library_id)
Foreign-key constraints:
    "class_knowledge_class_room_id_fkey" FOREIGN KEY (class_room_id) REFERENCES class_room(id) ON DELETE CASCADE
    "class_knowledge_created_by_user_id_fkey" FOREIGN KEY (created_by_user_id) REFERENCES user_profile(id)
    "class_knowledge_library_id_fkey" FOREIGN KEY (library_id) REFERENCES library(id) ON DELETE CASCADE
Access method: heap


\d+ public.class_message
                                               Table "public.class_message"
     Column     |  Type  | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
----------------+--------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id             | uuid   |           | not null | gen_random_uuid() | plain    |             |              | 
 user_id        | uuid   |           | not null |                   | plain    |             |              | 
 class_room_id  | uuid   |           | not null |                   | plain    |             |              | 
 parent_id      | uuid   |           |          |                   | plain    |             |              | 
 target_user_id | uuid   |           |          |                   | plain    |             |              | 
 content        | text   |           | not null |                   | extended |             |              | 
 data           | jsonb  |           |          | '{}'::jsonb       | extended |             |              | 
 meta           | jsonb  |           |          | '{}'::jsonb       | extended |             |              | 
 created_at     | bigint |           | not null | now_ms()          | plain    |             |              | 
 updated_at     | bigint |           | not null | now_ms()          | plain    |             |              | 
Indexes:
    "class_message_pkey" PRIMARY KEY, btree (id)
    "idx_class_message_parent" btree (parent_id, created_at) WHERE parent_id IS NOT NULL
    "idx_class_message_room" btree (class_room_id)
    "idx_class_message_room_created" btree (class_room_id, created_at DESC)
    "idx_class_message_user" btree (user_id, created_at DESC)
Foreign-key constraints:
    "class_message_class_room_id_fkey" FOREIGN KEY (class_room_id) REFERENCES class_room(id) ON DELETE CASCADE
    "class_message_parent_id_fkey" FOREIGN KEY (parent_id) REFERENCES class_message(id) ON DELETE CASCADE
    "class_message_target_user_id_fkey" FOREIGN KEY (target_user_id) REFERENCES user_profile(id) ON DELETE CASCADE
    "class_message_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
Referenced by:
    TABLE "class_message" CONSTRAINT "class_message_parent_id_fkey" FOREIGN KEY (parent_id) REFERENCES class_message(id) ON DELETE CASCADE
    TABLE "class_message_reaction" CONSTRAINT "class_message_reaction_message_id_fkey" FOREIGN KEY (message_id) REFERENCES class_message(id) ON DELETE CASCADE
Triggers:
    trg_class_message_updated_at BEFORE UPDATE ON class_message FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap



\d+ public.class_message_reaction
                                        Table "public.class_message_reaction"
   Column   |  Type  | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
------------+--------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id         | uuid   |           | not null | gen_random_uuid() | plain    |             |              | 
 user_id    | uuid   |           | not null |                   | plain    |             |              | 
 message_id | uuid   |           | not null |                   | plain    |             |              | 
 name       | text   |           | not null |                   | extended |             |              | 
 created_at | bigint |           | not null | now_ms()          | plain    |             |              | 
Indexes:
    "class_message_reaction_pkey" PRIMARY KEY, btree (id)
    "class_message_reaction_message_id_user_id_name_key" UNIQUE CONSTRAINT, btree (message_id, user_id, name)
Foreign-key constraints:
    "class_message_reaction_message_id_fkey" FOREIGN KEY (message_id) REFERENCES class_message(id) ON DELETE CASCADE
    "class_message_reaction_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
Access method: heap



\d+ public.class_read_receipt
                                       Table "public.class_read_receipt"
    Column     |  Type  | Collation | Nullable | Default  | Storage | Compression | Stats target | Description 
---------------+--------+-----------+----------+----------+---------+-------------+--------------+-------------
 class_room_id | uuid   |           | not null |          | plain   |             |              | 
 user_id       | uuid   |           | not null |          | plain   |             |              | 
 last_read_at  | bigint |           | not null | now_ms() | plain   |             |              | 
Indexes:
    "class_read_receipt_pkey" PRIMARY KEY, btree (class_room_id, user_id)
    "idx_class_read_receipt_user" btree (user_id)
Foreign-key constraints:
    "class_read_receipt_class_room_id_fkey" FOREIGN KEY (class_room_id) REFERENCES class_room(id) ON DELETE CASCADE
    "class_read_receipt_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
Access method: heap


\d+ public.class_room
  Table "public.class_room"
       Column       |  Type   | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
--------------------+---------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id                 | uuid    |           | not null | gen_random_uuid() | plain    |             |              | 
 class_id           | uuid    |           | not null |                   | plain    |             |              | 
 created_by_user_id | uuid    |           | not null |                   | plain    |             |              | 
 name               | text    |           | not null |                   | extended |             |              | 
 channel_type       | text    |           |          |                   | extended |             |              | 
 description        | text    |           |          |                   | extended |             |              | 
 data               | jsonb   |           |          | '{}'::jsonb       | extended |             |              | 
 meta               | jsonb   |           |          | '{}'::jsonb       | extended |             |              | 
 access_control     | jsonb   |           |          | '{}'::jsonb       | extended |             |              | 
 is_archived        | boolean |           | not null | false             | plain    |             |              | 
 created_at         | bigint  |           | not null | now_ms()          | plain    |             |              | 
 updated_at         | bigint  |           | not null | now_ms()          | plain    |             |              | 
Indexes:
    "class_room_pkey" PRIMARY KEY, btree (id)
    "idx_class_room_class" btree (class_id)
    "ux_class_room_class_name" UNIQUE, btree (class_id, lower(name))
Foreign-key constraints:
    "class_room_class_id_fkey" FOREIGN KEY (class_id) REFERENCES user_group(id) ON DELETE CASCADE
    "class_room_created_by_user_id_fkey" FOREIGN KEY (created_by_user_id) REFERENCES user_profile(id)
Referenced by:
    TABLE "class_assistant" CONSTRAINT "class_assistant_class_room_id_fkey" FOREIGN KEY (class_room_id) REFERENCES class_room(id) ON DELETE CASCADE
    TABLE "class_knowledge" CONSTRAINT "class_knowledge_class_room_id_fkey" FOREIGN KEY (class_room_id) REFERENCES class_room(id) ON DELETE CASCADE
    TABLE "class_message" CONSTRAINT "class_message_class_room_id_fkey" FOREIGN KEY (class_room_id) REFERENCES class_room(id) ON DELETE CASCADE
    TABLE "class_read_receipt" CONSTRAINT "class_read_receipt_class_room_id_fkey" FOREIGN KEY (class_room_id) REFERENCES class_room(id) ON DELETE CASCADE
    TABLE "class_room_member" CONSTRAINT "class_room_member_class_room_id_fkey" FOREIGN KEY (class_room_id) REFERENCES class_room(id) ON DELETE CASCADE


\d+ public.class_room_member
                                       Table "public.class_room_member"
    Column     |  Type  | Collation | Nullable | Default  | Storage | Compression | Stats target | Description 
---------------+--------+-----------+----------+----------+---------+-------------+--------------+-------------
 class_room_id | uuid   |           | not null |          | plain   |             |              | 
 user_id       | uuid   |           | not null |          | plain   |             |              | 
 created_at    | bigint |           | not null | now_ms() | plain   |             |              | 
Indexes:
    "class_room_member_pkey" PRIMARY KEY, btree (class_room_id, user_id)
Foreign-key constraints:
    "class_room_member_class_room_id_fkey" FOREIGN KEY (class_room_id) REFERENCES class_room(id) ON DELETE CASCADE
    "class_room_member_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
Access method: heap


\d+ public.created_model
                                               Table "public.created_model"
     Column     |  Type   | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
----------------+---------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id             | uuid    |           | not null | gen_random_uuid() | plain    |             |              | 
 user_id        | uuid    |           | not null |                   | plain    |             |              | 
 base_model_id  | text    |           |          |                   | extended |             |              | 
 name           | text    |           | not null |                   | extended |             |              | 
 params         | jsonb   |           |          | '{}'::jsonb       | extended |             |              | 
 meta           | jsonb   |           |          | '{}'::jsonb       | extended |             |              | 
 access_control | jsonb   |           |          | '{}'::jsonb       | extended |             |              | 
 is_active      | boolean |           | not null | true              | plain    |             |              | 
 created_at     | bigint  |           | not null | now_ms()          | plain    |             |              | 
 updated_at     | bigint  |           | not null | now_ms()          | plain    |             |              | 
Indexes:
    "created_model_pkey" PRIMARY KEY, btree (id)
    "ux_created_model_owner_name" UNIQUE, btree (user_id, lower(name))
Foreign-key constraints:
    "created_model_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
Referenced by:
    TABLE "mcp_server_binding" CONSTRAINT "mcp_server_binding_model_id_fkey" FOREIGN KEY (model_id) REFERENCES created_model(id) ON DELETE CASCADE
    TABLE "model_capability" CONSTRAINT "model_capability_model_id_fkey" FOREIGN KEY (model_id) REFERENCES created_model(id) ON DELETE CASCADE
    TABLE "model_library" CONSTRAINT "model_library_model_id_fkey" FOREIGN KEY (model_id) REFERENCES created_model(id) ON DELETE CASCADE
    TABLE "model_mcp_tool" CONSTRAINT "model_mcp_tool_model_id_fkey" FOREIGN KEY (model_id) REFERENCES created_model(id) ON DELETE CASCADE
    TABLE "model_tool" CONSTRAINT "model_tool_model_id_fkey" FOREIGN KEY (model_id) REFERENCES created_model(id) ON DELETE CASCADE
    TABLE "platform_capability_scope" CONSTRAINT "platform_capability_scope_model_id_fkey" FOREIGN KEY (model_id) REFERENCES created_model(id) ON DELETE CASCADE
Triggers:
    trg_created_model_updated_at BEFORE UPDATE ON created_model FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap


\d+ public.created_prompt
                                                Table "public.created_prompt"
     Column     |         Type          | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
----------------+-----------------------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id             | uuid                  |           | not null | gen_random_uuid() | plain    |             |              | 
 command        | character varying(64) |           | not null |                   | extended |             |              | 
 user_id        | uuid                  |           | not null |                   | plain    |             |              | 
 title          | text                  |           |          |                   | extended |             |              | 
 content        | text                  |           | not null |                   | extended |             |              | 
 variables      | jsonb                 |           |          | '{}'::jsonb       | extended |             |              | 
 access_control | jsonb                 |           |          | '{}'::jsonb       | extended |             |              | 
 created_at     | bigint                |           | not null | now_ms()          | plain    |             |              | 
 updated_at     | bigint                |           | not null | now_ms()          | plain    |             |              | 
Indexes:
    "created_prompt_pkey" PRIMARY KEY, btree (id)
    "ux_created_prompt_user_cmd" UNIQUE, btree (user_id, lower(command::text))
Check constraints:
    "created_prompt_command_check" CHECK (command::text ~ '^/'::text)
Foreign-key constraints:
    "created_prompt_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
Triggers:
    trg_created_prompt_updated_at BEFORE UPDATE ON created_prompt FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap


\d+ public.created_tool
                                                Table "public.created_tool"
     Column      |  Type   | Collation | Nullable |      Default       | Storage  | Compression | Stats target | Description 
-----------------+---------+-----------+----------+--------------------+----------+-------------+--------------+-------------
 id              | uuid    |           | not null | gen_random_uuid()  | plain    |             |              | 
 user_id         | uuid    |           | not null |                    | plain    |             |              | 
 name            | text    |           | not null |                    | extended |             |              | 
 slug            | text    |           | not null |                    | extended |             |              | 
 language        | text    |           | not null | 'python'::text     | extended |             |              | 
 entrypoint      | text    |           |          |                    | extended |             |              | 
 content         | text    |           | not null |                    | extended |             |              | 
 requirements    | text    |           |          |                    | extended |             |              | 
 sandbox_profile | text    |           | not null | 'restricted'::text | extended |             |              | 
 timeout_ms      | integer |           | not null | 60000              | plain    |             |              | 
 memory_limit_mb | integer |           | not null | 512                | plain    |             |              | 
 meta            | jsonb   |           |          | '{}'::jsonb        | extended |             |              | 
 valves          | jsonb   |           |          | '{}'::jsonb        | extended |             |              | 
 access_control  | jsonb   |           |          | '{}'::jsonb        | extended |             |              | 
 is_active       | boolean |           | not null | true               | plain    |             |              | 
 created_at      | bigint  |           | not null | now_ms()           | plain    |             |              | 
 updated_at      | bigint  |           | not null | now_ms()           | plain    |             |              | 
Indexes:
    "created_tool_pkey" PRIMARY KEY, btree (id)
    "idx_created_tool_user" btree (user_id)
    "ux_created_tool_owner_slug" UNIQUE, btree (user_id, lower(slug))
Check constraints:
    "created_tool_language_check" CHECK (language = 'python'::text)
    "created_tool_memory_limit_mb_check" CHECK (memory_limit_mb >= 64 AND memory_limit_mb <= 8192)
    "created_tool_sandbox_profile_check" CHECK (sandbox_profile = ANY (ARRAY['restricted'::text, 'networked'::text, 'gpu'::text]))
    "created_tool_timeout_ms_check" CHECK (timeout_ms >= 1 AND timeout_ms <= 600000)
Foreign-key constraints:
    "created_tool_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
Referenced by:
    TABLE "created_tool_version" CONSTRAINT "created_tool_version_tool_id_fkey" FOREIGN KEY (tool_id) REFERENCES created_tool(id) ON DELETE CASCADE
    TABLE "model_tool" CONSTRAINT "model_tool_tool_id_fkey" FOREIGN KEY (tool_id) REFERENCES created_tool(id) ON DELETE CASCADE
Triggers:
    trg_created_tool_updated_at BEFORE UPDATE ON created_tool FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap


\d+ public.created_tool_version
                                           Table "public.created_tool_version"
    Column    |  Type   | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
--------------+---------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id           | uuid    |           | not null | gen_random_uuid() | plain    |             |              | 
 tool_id      | uuid    |           | not null |                   | plain    |             |              | 
 version      | integer |           | not null |                   | plain    |             |              | 
 content      | text    |           | not null |                   | extended |             |              | 
 requirements | text    |           |          |                   | extended |             |              | 
 meta         | jsonb   |           |          | '{}'::jsonb       | extended |             |              | 
 created_at   | bigint  |           | not null | now_ms()          | plain    |             |              | 
Indexes:
    "created_tool_version_pkey" PRIMARY KEY, btree (id)
    "created_tool_version_tool_id_version_key" UNIQUE CONSTRAINT, btree (tool_id, version)
Foreign-key constraints:
    "created_tool_version_tool_id_fkey" FOREIGN KEY (tool_id) REFERENCES created_tool(id) ON DELETE CASCADE
Access method: heap




\d+ public.document_chunk
                                            Table "public.document_chunk"
   Column    |    Type     | Collation | Nullable |                                           Default                                           | Storage  | Compression | Stats target | Description 
-------------+-------------+-----------+----------+---------------------------------------------------------------------------------------------+----------+-------------+--------------+-------------
 id          | uuid        |           | not null | gen_random_uuid()                                                                           | plain    |             |              | 
 document_id | uuid        |           | not null |                                                                                             | plain    |             |              | 
 chunk_index | integer     |           | not null |                                                                                             | plain    |             |              | 
 content     | text        |           | not null |                                                                                             | extended |             |              | 
 embedding   | vector(768) |           | not null |                                                                                             | external |             |              | 
 token_count | integer     |           |          |                                                                                             | plain    |             |              | 
 meta        | jsonb       |           |          |                                                                                             | extended |             |              | 
 created_at  | bigint      |           | not null | now_ms()                                                                                    | plain    |             |              | 
 content_tsv | tsvector    |           |          | generated always as (to_tsvector('english'::regconfig, COALESCE(content, ''::text))) stored | extended |             |              | 
Indexes:
    "document_chunk_pkey" PRIMARY KEY, btree (id)
    "idx_document_chunk_doc" btree (document_id)
    "idx_document_chunk_embedding_hnsw" hnsw (embedding vector_cosine_ops)
    "idx_document_chunk_tsv_gin" gin (content_tsv)
    "idx_document_chunk_unique" UNIQUE, btree (document_id, chunk_index)
Check constraints:
    "document_chunk_chunk_index_check" CHECK (chunk_index >= 0)
Foreign-key constraints:
    "document_chunk_document_id_fkey" FOREIGN KEY (document_id) REFERENCES library_document(id) ON DELETE CASCADE
Access method: heap


\d+ public.library
                                                  Table "public.library"
     Column     |  Type  | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
----------------+--------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id             | uuid   |           | not null | gen_random_uuid() | plain    |             |              | 
 user_id        | uuid   |           | not null |                   | plain    |             |              | 
 name           | text   |           | not null |                   | extended |             |              | 
 description    | text   |           |          |                   | extended |             |              | 
 data           | jsonb  |           |          | '{}'::jsonb       | extended |             |              | 
 meta           | jsonb  |           |          | '{}'::jsonb       | extended |             |              | 
 access_control | jsonb  |           |          | '{}'::jsonb       | extended |             |              | 
 created_at     | bigint |           | not null | now_ms()          | plain    |             |              | 
 updated_at     | bigint |           | not null | now_ms()          | plain    |             |              | 
Indexes:
    "library_pkey" PRIMARY KEY, btree (id)
    "idx_library_user" btree (user_id)
Foreign-key constraints:
    "library_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
Referenced by:
    TABLE "class_knowledge" CONSTRAINT "class_knowledge_library_id_fkey" FOREIGN KEY (library_id) REFERENCES library(id) ON DELETE CASCADE
    TABLE "library_document" CONSTRAINT "library_document_library_id_fkey" FOREIGN KEY (library_id) REFERENCES library(id) ON DELETE CASCADE
    TABLE "library_file" CONSTRAINT "library_file_library_id_fkey" FOREIGN KEY (library_id) REFERENCES library(id) ON DELETE CASCADE
    TABLE "model_library" CONSTRAINT "model_library_library_id_fkey" FOREIGN KEY (library_id) REFERENCES library(id) ON DELETE CASCADE
Triggers:
    trg_library_updated_at BEFORE UPDATE ON library FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap



\d+ public.library_document
                                        Table "public.library_document"
   Column   |  Type  | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
------------+--------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id         | uuid   |           | not null | gen_random_uuid() | plain    |             |              | 
 library_id | uuid   |           | not null |                   | plain    |             |              | 
 source     | text   |           |          |                   | extended |             |              | 
 uri        | text   |           |          |                   | extended |             |              | 
 title      | text   |           |          |                   | extended |             |              | 
 meta       | jsonb  |           |          | '{}'::jsonb       | extended |             |              | 
 created_at | bigint |           | not null | now_ms()          | plain    |             |              | 
 updated_at | bigint |           | not null | now_ms()          | plain    |             |              | 
Indexes:
    "library_document_pkey" PRIMARY KEY, btree (id)
    "idx_library_document_library" btree (library_id)
Foreign-key constraints:
    "library_document_library_id_fkey" FOREIGN KEY (library_id) REFERENCES library(id) ON DELETE CASCADE
Referenced by:
    TABLE "document_chunk" CONSTRAINT "document_chunk_document_id_fkey" FOREIGN KEY (document_id) REFERENCES library_document(id) ON DELETE CASCADE
Triggers:
    trg_library_document_updated_at BEFORE UPDATE ON library_document FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap


\d+ public.library_file
                                        Table "public.library_file"
   Column   |  Type  | Collation | Nullable | Default  | Storage | Compression | Stats target | Description 
------------+--------+-----------+----------+----------+---------+-------------+--------------+-------------
 library_id | uuid   |           | not null |          | plain   |             |              | 
 file_id    | uuid   |           | not null |          | plain   |             |              | 
 created_at | bigint |           | not null | now_ms() | plain   |             |              | 
Indexes:
    "library_file_pkey" PRIMARY KEY, btree (library_id, file_id)
    "idx_library_file_file" btree (file_id)
Foreign-key constraints:
    "library_file_file_id_fkey" FOREIGN KEY (file_id) REFERENCES user_file(id) ON DELETE CASCADE
    "library_file_library_id_fkey" FOREIGN KEY (library_id) REFERENCES library(id) ON DELETE CASCADE
Access method: heap


\d+ public.mcp_server
                                                    Table "public.mcp_server"
        Column        |  Type   | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
----------------------+---------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id                   | uuid    |           | not null | gen_random_uuid() | plain    |             |              | 
 owner_user_id        | uuid    |           |          |                   | plain    |             |              | 
 organization_id      | uuid    |           |          |                   | plain    |             |              | 
 name                 | text    |           | not null |                   | extended |             |              | 
 slug                 | text    |           |          |                   | extended |             |              | 
 transport            | text    |           | not null |                   | extended |             |              | 
 command              | text    |           |          |                   | extended |             |              | 
 args                 | jsonb   |           |          |                   | extended |             |              | 
 env                  | jsonb   |           |          |                   | extended |             |              | 
 working_dir          | text    |           |          |                   | extended |             |              | 
 sse_url              | text    |           |          |                   | extended |             |              | 
 headers              | jsonb   |           |          |                   | extended |             |              | 
 auth_kind            | text    |           | not null | 'none'::text      | extended |             |              | 
 credential_id        | uuid    |           |          |                   | plain    |             |              | 
 timeouts             | jsonb   |           |          |                   | extended |             |              | 
 is_enabled           | boolean |           | not null | true              | plain    |             |              | 
 health_status        | text    |           | not null | 'unknown'::text   | extended |             |              | 
 last_seen_at         | bigint  |           |          |                   | plain    |             |              | 
 last_error           | text    |           |          |                   | extended |             |              | 
 provider_kind        | text    |           | not null | 'external'::text  | extended |             |              | 
 is_verified_provider | boolean |           | not null | false             | plain    |             |              | 
 certification        | jsonb   |           |          |                   | extended |             |              | 
 meta                 | jsonb   |           |          |                   | extended |             |              | 
 created_at           | bigint  |           | not null | now_ms()          | plain    |             |              | 
 updated_at           | bigint  |           | not null | now_ms()          | plain    |             |              | 
Indexes:
    "mcp_server_pkey" PRIMARY KEY, btree (id)
    "idx_mcp_server_org" btree (organization_id)
    "ux_mcp_server_owner_slug" UNIQUE, btree (owner_user_id, lower(COALESCE(slug, name)))
Check constraints:
    "mcp_server_auth_kind_check" CHECK (auth_kind = ANY (ARRAY['none'::text, 'bearer'::text, 'basic'::text, 'header'::text]))
    "mcp_server_health_status_check" CHECK (health_status = ANY (ARRAY['unknown'::text, 'healthy'::text, 'unreachable'::text, 'error'::text]))
    "mcp_server_provider_kind_check" CHECK (provider_kind = ANY (ARRAY['internal'::text, 'external'::text]))
    "mcp_server_transport_check" CHECK (transport = ANY (ARRAY['stdio'::text, 'sse'::text]))
Foreign-key constraints:
    "mcp_server_credential_id_fkey" FOREIGN KEY (credential_id) REFERENCES provider_credential(id) ON DELETE SET NULL
    "mcp_server_organization_id_fkey" FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE
    "mcp_server_owner_user_id_fkey" FOREIGN KEY (owner_user_id) REFERENCES user_profile(id) ON DELETE CASCADE
Referenced by:
    TABLE "mcp_server_binding" CONSTRAINT "mcp_server_binding_server_id_fkey" FOREIGN KEY (server_id) REFERENCES mcp_server(id) ON DELETE CASCADE
    TABLE "mcp_server_tool" CONSTRAINT "mcp_server_tool_server_id_fkey" FOREIGN KEY (server_id) REFERENCES mcp_server(id) ON DELETE CASCADE
    TABLE "mcp_server_version" CONSTRAINT "mcp_server_version_server_id_fkey" FOREIGN KEY (server_id) REFERENCES mcp_server(id) ON DELETE CASCADE
    TABLE "model_mcp_tool" CONSTRAINT "model_mcp_tool_server_id_fkey" FOREIGN KEY (server_id) REFERENCES mcp_server(id) ON DELETE CASCADE
Triggers:
    trg_mcp_server_updated_at BEFORE UPDATE ON mcp_server FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap


\d+ public.mcp_server_binding
                                             Table "public.mcp_server_binding"
     Column      |  Type   | Collation | Nullable |      Default      | Storage | Compression | Stats target | Description 
-----------------+---------+-----------+----------+-------------------+---------+-------------+--------------+-------------
 id              | uuid    |           | not null | gen_random_uuid() | plain   |             |              | 
 server_id       | uuid    |           | not null |                   | plain   |             |              | 
 organization_id | uuid    |           |          |                   | plain   |             |              | 
 class_room_id   | uuid    |           |          |                   | plain   |             |              | 
 model_id        | uuid    |           |          |                   | plain   |             |              | 
 assistant_id    | uuid    |           |          |                   | plain   |             |              | 
 enabled         | boolean |           | not null | true              | plain   |             |              | 
 precedence      | integer |           | not null | 0                 | plain   |             |              | 
 created_at      | bigint  |           | not null | now_ms()          | plain   |             |              | 
 updated_at      | bigint  |           | not null | now_ms()          | plain   |             |              | 
Indexes:
    "mcp_server_binding_pkey" PRIMARY KEY, btree (id)
    "idx_mcp_server_binding_prec" btree (server_id, precedence DESC)
    "idx_mcp_server_binding_server" btree (server_id)
    "ux_mcp_server_binding_scope" UNIQUE, btree (server_id, organization_id, class_room_id, model_id, assistant_id)
Check constraints:
    "mcp_server_binding_check" CHECK (((organization_id IS NOT NULL)::integer + (class_room_id IS NOT NULL)::integer + (model_id IS NOT NULL)::integer + (assistant_id IS NOT NULL)::integer) <= 1)
Foreign-key constraints:
    "mcp_server_binding_assistant_id_fkey" FOREIGN KEY (assistant_id) REFERENCES class_assistant(id) ON DELETE CASCADE
    "mcp_server_binding_class_room_id_fkey" FOREIGN KEY (class_room_id) REFERENCES class_room(id) ON DELETE CASCADE
    "mcp_server_binding_model_id_fkey" FOREIGN KEY (model_id) REFERENCES created_model(id) ON DELETE CASCADE
    "mcp_server_binding_organization_id_fkey" FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE
    "mcp_server_binding_server_id_fkey" FOREIGN KEY (server_id) REFERENCES mcp_server(id) ON DELETE CASCADE
Triggers:
    trg_mcp_server_binding_updated_at BEFORE UPDATE ON mcp_server_binding FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap



\d+ public.mcp_server_tool
                                                Table "public.mcp_server_tool"
       Column       |  Type   | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
--------------------+---------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id                 | uuid    |           | not null | gen_random_uuid() | plain    |             |              | 
 server_id          | uuid    |           | not null |                   | plain    |             |              | 
 name               | text    |           | not null |                   | extended |             |              | 
 description        | text    |           |          |                   | extended |             |              | 
 input_schema       | jsonb   |           | not null |                   | extended |             |              | 
 is_enabled         | boolean |           | not null | true              | plain    |             |              | 
 last_discovered_at | bigint  |           | not null | now_ms()          | plain    |             |              | 
 created_at         | bigint  |           | not null | now_ms()          | plain    |             |              | 
Indexes:
    "mcp_server_tool_pkey" PRIMARY KEY, btree (id)
    "idx_mcp_server_tool_server" btree (server_id)
    "ux_mcp_server_tool_name" UNIQUE, btree (server_id, lower(name))
Foreign-key constraints:
    "mcp_server_tool_server_id_fkey" FOREIGN KEY (server_id) REFERENCES mcp_server(id) ON DELETE CASCADE
Access method: heap


\d+ public.mcp_server_version
                                           Table "public.mcp_server_version"
   Column   |  Type   | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
------------+---------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id         | uuid    |           | not null | gen_random_uuid() | plain    |             |              | 
 server_id  | uuid    |           | not null |                   | plain    |             |              | 
 version    | integer |           | not null |                   | plain    |             |              | 
 spec       | jsonb   |           | not null |                   | extended |             |              | 
 created_at | bigint  |           | not null | now_ms()          | plain    |             |              | 
Indexes:
    "mcp_server_version_pkey" PRIMARY KEY, btree (id)
    "mcp_server_version_server_id_version_key" UNIQUE CONSTRAINT, btree (server_id, version)
Foreign-key constraints:
    "mcp_server_version_server_id_fkey" FOREIGN KEY (server_id) REFERENCES mcp_server(id) ON DELETE CASCADE
Access method: heap


\d+ public.model_capability
                                         Table "public.model_capability"
    Column     |  Type   | Collation | Nullable | Default  | Storage  | Compression | Stats target | Description 
---------------+---------+-----------+----------+----------+----------+-------------+--------------+-------------
 model_id      | uuid    |           | not null |          | plain    |             |              | 
 capability_id | uuid    |           | not null |          | plain    |             |              | 
 enabled       | boolean |           | not null | true     | plain    |             |              | 
 precedence    | integer |           | not null | 0        | plain    |             |              | 
 config        | jsonb   |           |          |          | extended |             |              | 
 created_at    | bigint  |           | not null | now_ms() | plain    |             |              | 
Indexes:
    "model_capability_pkey" PRIMARY KEY, btree (model_id, capability_id)
    "idx_model_capability_cap" btree (capability_id)
Foreign-key constraints:
    "model_capability_capability_id_fkey" FOREIGN KEY (capability_id) REFERENCES platform_capability(id) ON DELETE CASCADE
    "model_capability_model_id_fkey" FOREIGN KEY (model_id) REFERENCES created_model(id) ON DELETE CASCADE
Access method: heap


\d+ public.model_library
                                           Table "public.model_library"
   Column    |  Type   | Collation | Nullable |   Default   | Storage  | Compression | Stats target | Description 
-------------+---------+-----------+----------+-------------+----------+-------------+--------------+-------------
 model_id    | uuid    |           | not null |             | plain    |             |              | 
 library_id  | uuid    |           | not null |             | plain    |             |              | 
 order_index | integer |           |          |             | plain    |             |              | 
 retrieval   | jsonb   |           |          | '{}'::jsonb | extended |             |              | 
Indexes:
    "model_library_pkey" PRIMARY KEY, btree (model_id, library_id)
    "idx_model_library_library" btree (library_id)
Foreign-key constraints:
    "model_library_library_id_fkey" FOREIGN KEY (library_id) REFERENCES library(id) ON DELETE CASCADE
    "model_library_model_id_fkey" FOREIGN KEY (model_id) REFERENCES created_model(id) ON DELETE CASCADE
Access method: heap


\d+ public.model_mcp_tool
                                         Table "public.model_mcp_tool"
   Column    |  Type   | Collation | Nullable | Default  | Storage  | Compression | Stats target | Description 
-------------+---------+-----------+----------+----------+----------+-------------+--------------+-------------
 model_id    | uuid    |           | not null |          | plain    |             |              | 
 server_id   | uuid    |           | not null |          | plain    |             |              | 
 tool_name   | text    |           | not null |          | extended |             |              | 
 order_index | integer |           |          |          | plain    |             |              | 
 config      | jsonb   |           |          |          | extended |             |              | 
 enabled     | boolean |           | not null | true     | plain    |             |              | 
 created_at  | bigint  |           | not null | now_ms() | plain    |             |              | 
Indexes:
    "model_mcp_tool_pkey" PRIMARY KEY, btree (model_id, server_id, tool_name)
    "idx_model_mcp_tool_server" btree (server_id)
Foreign-key constraints:
    "model_mcp_tool_model_id_fkey" FOREIGN KEY (model_id) REFERENCES created_model(id) ON DELETE CASCADE
    "model_mcp_tool_server_id_fkey" FOREIGN KEY (server_id) REFERENCES mcp_server(id) ON DELETE CASCADE
Access method: heap


\d+ public.model_provider
                                            Table "public.model_provider"
   Column   |  Type  | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
------------+--------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id         | uuid   |           | not null | gen_random_uuid() | plain    |             |              | 
 name       | text   |           | not null |                   | extended |             |              | 
 kind       | text   |           | not null |                   | extended |             |              | 
 config     | jsonb  |           |          | '{}'::jsonb       | extended |             |              | 
 created_at | bigint |           | not null | now_ms()          | plain    |             |              | 
 updated_at | bigint |           | not null | now_ms()          | plain    |             |              | 
Indexes:
    "model_provider_pkey" PRIMARY KEY, btree (id)
    "model_provider_name_key" UNIQUE CONSTRAINT, btree (name)
Referenced by:
    TABLE "base_model" CONSTRAINT "base_model_provider_id_fkey" FOREIGN KEY (provider_id) REFERENCES model_provider(id) ON DELETE CASCADE
    TABLE "provider_credential" CONSTRAINT "provider_credential_provider_id_fkey" FOREIGN KEY (provider_id) REFERENCES model_provider(id) ON DELETE CASCADE
Triggers:
    trg_model_provider_updated_at BEFORE UPDATE ON model_provider FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap


\d+ public.model_tool
                                            Table "public.model_tool"
   Column    |  Type   | Collation | Nullable |   Default   | Storage  | Compression | Stats target | Description 
-------------+---------+-----------+----------+-------------+----------+-------------+--------------+-------------
 model_id    | uuid    |           | not null |             | plain    |             |              | 
 tool_id     | uuid    |           | not null |             | plain    |             |              | 
 order_index | integer |           |          |             | plain    |             |              | 
 config      | jsonb   |           |          | '{}'::jsonb | extended |             |              | 
 enabled     | boolean |           | not null | true        | plain    |             |              | 
Indexes:
    "model_tool_pkey" PRIMARY KEY, btree (model_id, tool_id)
    "idx_model_tool_tool" btree (tool_id)
Foreign-key constraints:
    "model_tool_model_id_fkey" FOREIGN KEY (model_id) REFERENCES created_model(id) ON DELETE CASCADE
    "model_tool_tool_id_fkey" FOREIGN KEY (tool_id) REFERENCES created_tool(id) ON DELETE CASCADE
Access method: heap


\d+ public.organization
                                             Table "public.organization"
   Column   |  Type  | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
------------+--------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id         | uuid   |           | not null | gen_random_uuid() | plain    |             |              | 
 name       | text   |           | not null |                   | extended |             |              | 
 slug       | text   |           |          |                   | extended |             |              | 
 meta       | jsonb  |           |          | '{}'::jsonb       | extended |             |              | 
 created_at | bigint |           | not null | now_ms()          | plain    |             |              | 
 updated_at | bigint |           | not null | now_ms()          | plain    |             |              | 
Indexes:
    "organization_pkey" PRIMARY KEY, btree (id)
    "organization_slug_key" UNIQUE CONSTRAINT, btree (slug)
Referenced by:
    TABLE "mcp_server_binding" CONSTRAINT "mcp_server_binding_organization_id_fkey" FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE
    TABLE "mcp_server" CONSTRAINT "mcp_server_organization_id_fkey" FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE
    TABLE "organization_domain" CONSTRAINT "organization_domain_organization_id_fkey" FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE
    TABLE "organization_idp" CONSTRAINT "organization_idp_organization_id_fkey" FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE
    TABLE "platform_capability_scope" CONSTRAINT "platform_capability_scope_organization_id_fkey" FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE
    TABLE "provider_credential" CONSTRAINT "provider_credential_organization_id_fkey" FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE
Triggers:
    trg_organization_updated_at BEFORE UPDATE ON organization FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap



\d+ public.organization_domain
                                             Table "public.organization_domain"
     Column      |  Type   | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
-----------------+---------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id              | uuid    |           | not null | gen_random_uuid() | plain    |             |              | 
 organization_id | uuid    |           | not null |                   | plain    |             |              | 
 domain          | text    |           | not null |                   | extended |             |              | 
 verified        | boolean |           | not null | false             | plain    |             |              | 
 created_at      | bigint  |           | not null | now_ms()          | plain    |             |              | 
 updated_at      | bigint  |           | not null | now_ms()          | plain    |             |              | 
Indexes:
    "organization_domain_pkey" PRIMARY KEY, btree (id)
    "ux_org_domain_lower" UNIQUE, btree (lower(domain))
Foreign-key constraints:
    "organization_domain_organization_id_fkey" FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE
Triggers:
    trg_organization_domain_updated_at BEFORE UPDATE ON organization_domain FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap


\d+ public.organization_idp
                                                Table "public.organization_idp"
     Column      |  Type   | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
-----------------+---------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id              | uuid    |           | not null | gen_random_uuid() | plain    |             |              | 
 organization_id | uuid    |           | not null |                   | plain    |             |              | 
 provider        | text    |           | not null |                   | extended |             |              | 
 config          | jsonb   |           | not null |                   | extended |             |              | 
 is_enabled      | boolean |           | not null | true              | plain    |             |              | 
 created_at      | bigint  |           | not null | now_ms()          | plain    |             |              | 
 updated_at      | bigint  |           | not null | now_ms()          | plain    |             |              | 
Indexes:
    "organization_idp_pkey" PRIMARY KEY, btree (id)
    "ux_org_provider_lower" UNIQUE, btree (organization_id, lower(provider))
Foreign-key constraints:
    "organization_idp_organization_id_fkey" FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE
Triggers:
    trg_organization_idp_updated_at BEFORE UPDATE ON organization_idp FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap


\d+ public.platform_capability
                                             Table "public.platform_capability"
    Column     |  Type  | Collation | Nullable |       Default        | Storage  | Compression | Stats target | Description 
---------------+--------+-----------+----------+----------------------+----------+-------------+--------------+-------------
 id            | uuid   |           | not null | gen_random_uuid()    | plain    |             |              | 
 key           | text   |           | not null |                      | extended |             |              | 
 description   | text   |           |          |                      | extended |             |              | 
 rollout_phase | text   |           | not null | 'experimental'::text | extended |             |              | 
 guardrails    | jsonb  |           |          |                      | extended |             |              | 
 meta          | jsonb  |           |          |                      | extended |             |              | 
 created_at    | bigint |           | not null | now_ms()             | plain    |             |              | 
 updated_at    | bigint |           | not null | now_ms()             | plain    |             |              | 
Indexes:
    "platform_capability_pkey" PRIMARY KEY, btree (id)
    "ux_platform_capability_key" UNIQUE, btree (lower(key))
Check constraints:
    "platform_capability_rollout_phase_check" CHECK (rollout_phase = ANY (ARRAY['experimental'::text, 'beta'::text, 'ga'::text, 'deprecated'::text]))
Referenced by:
    TABLE "model_capability" CONSTRAINT "model_capability_capability_id_fkey" FOREIGN KEY (capability_id) REFERENCES platform_capability(id) ON DELETE CASCADE
    TABLE "platform_capability_scope" CONSTRAINT "platform_capability_scope_capability_id_fkey" FOREIGN KEY (capability_id) REFERENCES platform_capability(id) ON DELETE CASCADE
Triggers:
    trg_platform_capability_updated_at BEFORE UPDATE ON platform_capability FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap



\d+ public.platform_capability_scope
                                        Table "public.platform_capability_scope"
     Column      |  Type   | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
-----------------+---------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id              | uuid    |           | not null | gen_random_uuid() | plain    |             |              | 
 capability_id   | uuid    |           | not null |                   | plain    |             |              | 
 organization_id | uuid    |           |          |                   | plain    |             |              | 
 class_room_id   | uuid    |           |          |                   | plain    |             |              | 
 model_id        | uuid    |           |          |                   | plain    |             |              | 
 assistant_id    | uuid    |           |          |                   | plain    |             |              | 
 scope_label     | text    |           |          |                   | extended |             |              | 
 enabled         | boolean |           | not null | true              | plain    |             |              | 
 precedence      | integer |           | not null | 0                 | plain    |             |              | 
 config          | jsonb   |           |          |                   | extended |             |              | 
 starts_at       | bigint  |           |          |                   | plain    |             |              | 
 ends_at         | bigint  |           |          |                   | plain    |             |              | 
 created_by      | uuid    |           |          |                   | plain    |             |              | 
 created_at      | bigint  |           | not null | now_ms()          | plain    |             |              | 
 updated_at      | bigint  |           | not null | now_ms()          | plain    |             |              | 
Indexes:
    "platform_capability_scope_pkey" PRIMARY KEY, btree (id)
    "idx_platform_capability_scope_assistant" btree (assistant_id) WHERE assistant_id IS NOT NULL
    "idx_platform_capability_scope_cap" btree (capability_id)
    "idx_platform_capability_scope_model" btree (model_id) WHERE model_id IS NOT NULL
    "idx_platform_capability_scope_org" btree (organization_id) WHERE organization_id IS NOT NULL
    "idx_platform_capability_scope_prec" btree (capability_id, precedence DESC)
    "idx_platform_capability_scope_room" btree (class_room_id) WHERE class_room_id IS NOT NULL
    "ux_platform_capability_scope" UNIQUE, btree (capability_id, organization_id, class_room_id, model_id, assistant_id)
Check constraints:
    "platform_capability_scope_check" CHECK (((organization_id IS NOT NULL)::integer + (class_room_id IS NOT NULL)::integer + (model_id IS NOT NULL)::integer + (assistant_id IS NOT NULL)::integer) <= 1)
Foreign-key constraints:
    "platform_capability_scope_assistant_id_fkey" FOREIGN KEY (assistant_id) REFERENCES class_assistant(id) ON DELETE CASCADE
    "platform_capability_scope_capability_id_fkey" FOREIGN KEY (capability_id) REFERENCES platform_capability(id) ON DELETE CASCADE
    "platform_capability_scope_class_room_id_fkey" FOREIGN KEY (class_room_id) REFERENCES class_room(id) ON DELETE CASCADE
    "platform_capability_scope_created_by_fkey" FOREIGN KEY (created_by) REFERENCES user_profile(id) ON DELETE SET NULL
    "platform_capability_scope_model_id_fkey" FOREIGN KEY (model_id) REFERENCES created_model(id) ON DELETE CASCADE
    "platform_capability_scope_organization_id_fkey" FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE
Triggers:
    trg_platform_capability_scope_updated_at BEFORE UPDATE ON platform_capability_scope FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap



\d+ public.platform_feature_flag
                                      Table "public.platform_feature_flag"
    Column    |  Type   | Collation | Nullable | Default  | Storage  | Compression | Stats target | Description 
--------------+---------+-----------+----------+----------+----------+-------------+--------------+-------------
 key          | text    |           | not null |          | extended |             |              | 
 is_enabled   | boolean |           | not null | false    | plain    |             |              | 
 effective_at | bigint  |           |          |          | plain    |             |              | 
 sticky       | boolean |           | not null | false    | plain    |             |              | 
 description  | text    |           |          |          | extended |             |              | 
 meta         | jsonb   |           |          |          | extended |             |              | 
 created_at   | bigint  |           | not null | now_ms() | plain    |             |              | 
 updated_at   | bigint  |           | not null | now_ms() | plain    |             |              | 
Indexes:
    "platform_feature_flag_pkey" PRIMARY KEY, btree (key)
Triggers:
    trg_platform_feature_flag_updated_at BEFORE UPDATE ON platform_feature_flag FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap


\d+ public.provider_credential
                                            Table "public.provider_credential"
     Column      |  Type  | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
-----------------+--------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id              | uuid   |           | not null | gen_random_uuid() | plain    |             |              | 
 user_id         | uuid   |           |          |                   | plain    |             |              | 
 organization_id | uuid   |           |          |                   | plain    |             |              | 
 provider_id     | uuid   |           | not null |                   | plain    |             |              | 
 name            | text   |           | not null |                   | extended |             |              | 
 secret_ref      | text   |           | not null |                   | extended |             |              | 
 created_at      | bigint |           | not null | now_ms()          | plain    |             |              | 
 updated_at      | bigint |           | not null | now_ms()          | plain    |             |              | 
Indexes:
    "provider_credential_pkey" PRIMARY KEY, btree (id)
    "idx_provider_credential_org" btree (organization_id)
    "idx_provider_credential_provider" btree (provider_id)
    "idx_provider_credential_user" btree (user_id)
Foreign-key constraints:
    "provider_credential_organization_id_fkey" FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE
    "provider_credential_provider_id_fkey" FOREIGN KEY (provider_id) REFERENCES model_provider(id) ON DELETE CASCADE
    "provider_credential_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
Referenced by:
    TABLE "mcp_server" CONSTRAINT "mcp_server_credential_id_fkey" FOREIGN KEY (credential_id) REFERENCES provider_credential(id) ON DELETE SET NULL
Triggers:
    trg_provider_credential_updated_at BEFORE UPDATE ON provider_credential FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap


\d+ public.resource_shares
                                                  Table "public.resource_shares"
      Column      |     Type      | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
------------------+---------------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id               | uuid          |           | not null | gen_random_uuid() | plain    |             |              | 
 resource_type    | resource_kind |           | not null |                   | plain    |             |              | 
 resource_id      | uuid          |           | not null |                   | plain    |             |              | 
 grantee_group_id | uuid          |           |          |                   | plain    |             |              | 
 grantee_user_id  | uuid          |           |          |                   | plain    |             |              | 
 permission       | text          |           | not null |                   | extended |             |              | 
 created_by       | uuid          |           | not null |                   | plain    |             |              | 
 created_at       | bigint        |           | not null | now_ms()          | plain    |             |              | 
 expires_at       | bigint        |           |          |                   | plain    |             |              | 
Indexes:
    "resource_shares_pkey" PRIMARY KEY, btree (id)
    "ux_resource_share_target_grantee" UNIQUE, btree (resource_type, resource_id, grantee_group_id, grantee_user_id)
Check constraints:
    "resource_shares_check" CHECK ((grantee_group_id IS NULL) <> (grantee_user_id IS NULL))
    "resource_shares_permission_check" CHECK (permission = ANY (ARRAY['view'::text, 'use'::text, 'edit'::text, 'admin'::text]))
Foreign-key constraints:
    "resource_shares_created_by_fkey" FOREIGN KEY (created_by) REFERENCES user_profile(id) ON DELETE CASCADE
    "resource_shares_grantee_group_id_fkey" FOREIGN KEY (grantee_group_id) REFERENCES user_group(id) ON DELETE CASCADE
    "resource_shares_grantee_user_id_fkey" FOREIGN KEY (grantee_user_id) REFERENCES user_profile(id) ON DELETE CASCADE
Access method: heap


\d+ public.user_artifact
                                                 Table "public.user_artifact"
       Column       |  Type   | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
--------------------+---------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id                 | uuid    |           | not null | gen_random_uuid() | plain    |             |              | 
 user_id            | uuid    |           | not null |                   | plain    |             |              | 
 chat_id            | uuid    |           |          |                   | plain    |             |              | 
 group_id           | uuid    |           |          |                   | plain    |             |              | 
 title              | text    |           | not null |                   | extended |             |              | 
 type               | text    |           | not null |                   | extended |             |              | 
 language           | text    |           |          |                   | extended |             |              | 
 content            | text    |           | not null |                   | extended |             |              | 
 subject_area       | text    |           |          |                   | extended |             |              | 
 grade_level        | text    |           |          |                   | extended |             |              | 
 version            | integer |           | not null | 1                 | plain    |             |              | 
 parent_artifact_id | uuid    |           |          |                   | plain    |             |              | 
 meta               | jsonb   |           |          | '{}'::jsonb       | extended |             |              | 
 access_control     | jsonb   |           |          | '{}'::jsonb       | extended |             |              | 
 is_published       | boolean |           | not null | false             | plain    |             |              | 
 is_template        | boolean |           | not null | false             | plain    |             |              | 
 created_at         | bigint  |           | not null | now_ms()          | plain    |             |              | 
 updated_at         | bigint  |           | not null | now_ms()          | plain    |             |              | 
Indexes:
    "user_artifact_pkey" PRIMARY KEY, btree (id)
    "ux_user_artifact_lineage_version" UNIQUE, btree (COALESCE(parent_artifact_id, id), version)
Check constraints:
    "user_artifact_version_check" CHECK (version >= 1)
Foreign-key constraints:
    "user_artifact_chat_id_fkey" FOREIGN KEY (chat_id) REFERENCES user_chat(id) ON DELETE SET NULL
    "user_artifact_group_id_fkey" FOREIGN KEY (group_id) REFERENCES user_group(id) ON DELETE SET NULL
    "user_artifact_parent_artifact_id_fkey" FOREIGN KEY (parent_artifact_id) REFERENCES user_artifact(id) ON DELETE SET NULL
    "user_artifact_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
Referenced by:
    TABLE "user_artifact" CONSTRAINT "user_artifact_parent_artifact_id_fkey" FOREIGN KEY (parent_artifact_id) REFERENCES user_artifact(id) ON DELETE SET NULL
Triggers:
    trg_user_artifact_updated_at BEFORE UPDATE ON user_artifact FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap


\d+ public.user_auth
                                                      Table "public.user_auth"
          Column          |  Type   | Collation | Nullable |     Default      | Storage  | Compression | Stats target | Description 
--------------------------+---------+-----------+----------+------------------+----------+-------------+--------------+-------------
 id                       | uuid    |           | not null |                  | plain    |             |              | 
 email                    | citext  |           | not null |                  | extended |             |              | 
 password                 | text    |           |          |                  | extended |             |              | 
 is_active                | boolean |           | not null | true             | plain    |             |              | 
 created_at               | bigint  |           | not null | now_ms()         | plain    |             |              | 
 updated_at               | bigint  |           | not null | now_ms()         | plain    |             |              | 
 last_login_at            | bigint  |           |          |                  | plain    |             |              | 
 failed_attempts          | integer |           | not null | 0                | plain    |             |              | 
 locked_until             | bigint  |           |          |                  | plain    |             |              | 
 auth_method              | text    |           | not null | 'password'::text | extended |             |              | 
 requires_password_change | boolean |           | not null | false            | plain    |             |              | 
Indexes:
    "user_auth_pkey" PRIMARY KEY, btree (id)
    "user_auth_email_key" UNIQUE CONSTRAINT, btree (email)
Foreign-key constraints:
    "user_auth_id_fkey" FOREIGN KEY (id) REFERENCES user_profile(id) ON DELETE CASCADE
Triggers:
    trg_user_auth_updated_at BEFORE UPDATE ON user_auth FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap


\d+ public.user_chat
                                                Table "public.user_chat"
    Column    |  Type   | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
--------------+---------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id           | uuid    |           | not null | gen_random_uuid() | plain    |             |              | 
 user_id      | uuid    |           | not null |                   | plain    |             |              | 
 title        | text    |           |          |                   | extended |             |              | 
 conversation | jsonb   |           | not null |                   | extended |             |              | 
 share_id     | text    |           |          |                   | extended |             |              | 
 archived     | boolean |           | not null | false             | plain    |             |              | 
 pinned       | boolean |           |          | false             | plain    |             |              | 
 meta         | jsonb   |           |          | '{}'::jsonb       | extended |             |              | 
 folder_id    | uuid    |           |          |                   | plain    |             |              | 
 created_at   | bigint  |           | not null | now_ms()          | plain    |             |              | 
 updated_at   | bigint  |           | not null | now_ms()          | plain    |             |              | 
Indexes:
    "user_chat_pkey" PRIMARY KEY, btree (id)
    "idx_user_chat_user_pinned" btree (user_id, pinned, updated_at DESC) WHERE archived = false AND pinned = true
    "idx_user_chat_user_updated" btree (user_id, updated_at DESC) WHERE archived = false
    "user_chat_share_id_key" UNIQUE CONSTRAINT, btree (share_id)
Foreign-key constraints:
    "user_chat_folder_id_fkey" FOREIGN KEY (folder_id) REFERENCES user_folder(id) ON DELETE SET NULL
    "user_chat_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
Referenced by:
    TABLE "user_artifact" CONSTRAINT "user_artifact_chat_id_fkey" FOREIGN KEY (chat_id) REFERENCES user_chat(id) ON DELETE SET NULL
    TABLE "user_chat_tag" CONSTRAINT "user_chat_tag_chat_id_fkey" FOREIGN KEY (chat_id) REFERENCES user_chat(id) ON DELETE CASCADE
Policies:
    POLICY "user_chat_owner_only"
      USING ((user_id = (current_setting('app.user_id'::text, true))::uuid))
Triggers:
    trg_user_chat_updated_at BEFORE UPDATE ON user_chat FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap


\d+ public.user_chat_tag
                                                Table "public.user_chat"
    Column    |  Type   | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
--------------+---------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id           | uuid    |           | not null | gen_random_uuid() | plain    |             |              | 
 user_id      | uuid    |           | not null |                   | plain    |             |              | 
 title        | text    |           |          |                   | extended |             |              | 
 conversation | jsonb   |           | not null |                   | extended |             |              | 
 share_id     | text    |           |          |                   | extended |             |              | 
 archived     | boolean |           | not null | false             | plain    |             |              | 
 pinned       | boolean |           |          | false             | plain    |             |              | 
 meta         | jsonb   |           |          | '{}'::jsonb       | extended |             |              | 
 folder_id    | uuid    |           |          |                   | plain    |             |              | 
 created_at   | bigint  |           | not null | now_ms()          | plain    |             |              | 
 updated_at   | bigint  |           | not null | now_ms()          | plain    |             |              | 
Indexes:
    "user_chat_pkey" PRIMARY KEY, btree (id)
    "idx_user_chat_user_pinned" btree (user_id, pinned, updated_at DESC) WHERE archived = false AND pinned = true
    "idx_user_chat_user_updated" btree (user_id, updated_at DESC) WHERE archived = false
    "user_chat_share_id_key" UNIQUE CONSTRAINT, btree (share_id)
Foreign-key constraints:
    "user_chat_folder_id_fkey" FOREIGN KEY (folder_id) REFERENCES user_folder(id) ON DELETE SET NULL
    "user_chat_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
Referenced by:
    TABLE "user_artifact" CONSTRAINT "user_artifact_chat_id_fkey" FOREIGN KEY (chat_id) REFERENCES user_chat(id) ON DELETE SET NULL
    TABLE "user_chat_tag" CONSTRAINT "user_chat_tag_chat_id_fkey" FOREIGN KEY (chat_id) REFERENCES user_chat(id) ON DELETE CASCADE
Policies:
    POLICY "user_chat_owner_only"
      USING ((user_id = (current_setting('app.user_id'::text, true))::uuid))
Triggers:
    trg_user_chat_updated_at BEFORE UPDATE ON user_chat FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap

appdb=# \d+ public.user_chat_tag
                                             Table "public.user_chat_tag"
   Column   |  Type  | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
------------+--------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id         | uuid   |           | not null | gen_random_uuid() | plain    |             |              | 
 tag_name   | text   |           | not null |                   | extended |             |              | 
 chat_id    | uuid   |           | not null |                   | plain    |             |              | 
 user_id    | uuid   |           | not null |                   | plain    |             |              | 
 created_at | bigint |           | not null | now_ms()          | plain    |             |              | 
Indexes:
    "user_chat_tag_pkey" PRIMARY KEY, btree (id)
    "ux_user_chat_tag_user_chat_name" UNIQUE, btree (user_id, chat_id, lower(tag_name))
Foreign-key constraints:
    "user_chat_tag_chat_id_fkey" FOREIGN KEY (chat_id) REFERENCES user_chat(id) ON DELETE CASCADE
    "user_chat_tag_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
Access method: heap


\d+ public.user_feedback
                                             Table "public.user_feedback"
   Column   |  Type  | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
------------+--------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id         | uuid   |           | not null | gen_random_uuid() | plain    |             |              | 
 user_id    | uuid   |           | not null |                   | plain    |             |              | 
 version    | bigint |           | not null | 0                 | plain    |             |              | 
 type       | text   |           | not null |                   | extended |             |              | 
 data       | jsonb  |           |          |                   | extended |             |              | 
 meta       | jsonb  |           |          |                   | extended |             |              | 
 snapshot   | jsonb  |           |          |                   | extended |             |              | 
 created_at | bigint |           | not null | now_ms()          | plain    |             |              | 
 updated_at | bigint |           | not null | now_ms()          | plain    |             |              | 
Indexes:
    "user_feedback_pkey" PRIMARY KEY, btree (id)
Foreign-key constraints:
    "user_feedback_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
Triggers:
    trg_user_feedback_updated_at BEFORE UPDATE ON user_feedback FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap


\d+ public.user_file
                                                 Table "public.user_file"
     Column     |  Type  | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
----------------+--------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id             | uuid   |           | not null | gen_random_uuid() | plain    |             |              | 
 user_id        | uuid   |           | not null |                   | plain    |             |              | 
 hash           | text   |           |          |                   | extended |             |              | 
 filename       | text   |           | not null |                   | extended |             |              | 
 path           | text   |           |          |                   | extended |             |              | 
 data           | jsonb  |           |          | '{}'::jsonb       | extended |             |              | 
 meta           | jsonb  |           |          | '{}'::jsonb       | extended |             |              | 
 access_control | jsonb  |           |          | '{}'::jsonb       | extended |             |              | 
 created_at     | bigint |           | not null | now_ms()          | plain    |             |              | 
 updated_at     | bigint |           | not null | now_ms()          | plain    |             |              | 
Indexes:
    "user_file_pkey" PRIMARY KEY, btree (id)
    "idx_user_file_user" btree (user_id)
Foreign-key constraints:
    "user_file_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
Referenced by:
    TABLE "library_file" CONSTRAINT "library_file_file_id_fkey" FOREIGN KEY (file_id) REFERENCES user_file(id) ON DELETE CASCADE
Policies:
    POLICY "user_file_owner_only"
      USING ((user_id = (current_setting('app.user_id'::text, true))::uuid))
Triggers:
    trg_user_file_updated_at BEFORE UPDATE ON user_file FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap


\d+ public.user_folder
                                               Table "public.user_folder"
   Column    |  Type   | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
-------------+---------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id          | uuid    |           | not null | gen_random_uuid() | plain    |             |              | 
 parent_id   | uuid    |           |          |                   | plain    |             |              | 
 user_id     | uuid    |           | not null |                   | plain    |             |              | 
 name        | text    |           | not null |                   | extended |             |              | 
 items       | jsonb   |           |          | '{}'::jsonb       | extended |             |              | 
 meta        | jsonb   |           |          | '{}'::jsonb       | extended |             |              | 
 is_expanded | boolean |           | not null | false             | plain    |             |              | 
 created_at  | bigint  |           | not null | now_ms()          | plain    |             |              | 
 updated_at  | bigint  |           | not null | now_ms()          | plain    |             |              | 
Indexes:
    "user_folder_pkey" PRIMARY KEY, btree (id)
Foreign-key constraints:
    "user_folder_parent_id_fkey" FOREIGN KEY (parent_id) REFERENCES user_folder(id) ON DELETE CASCADE
    "user_folder_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
Referenced by:
    TABLE "user_chat" CONSTRAINT "user_chat_folder_id_fkey" FOREIGN KEY (folder_id) REFERENCES user_folder(id) ON DELETE SET NULL
    TABLE "user_folder" CONSTRAINT "user_folder_parent_id_fkey" FOREIGN KEY (parent_id) REFERENCES user_folder(id) ON DELETE CASCADE
Triggers:
    trg_user_folder_updated_at BEFORE UPDATE ON user_folder FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap


\d+ public.user_group
                                                Table "public.user_group"
    Column     |  Type  | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
---------------+--------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id            | uuid   |           | not null | gen_random_uuid() | plain    |             |              | 
 owner_user_id | uuid   |           | not null |                   | plain    |             |              | 
 name          | text   |           | not null |                   | extended |             |              | 
 description   | text   |           |          |                   | extended |             |              | 
 data          | jsonb  |           |          | '{}'::jsonb       | extended |             |              | 
 meta          | jsonb  |           |          | '{}'::jsonb       | extended |             |              | 
 created_at    | bigint |           | not null | now_ms()          | plain    |             |              | 
 updated_at    | bigint |           | not null | now_ms()          | plain    |             |              | 
Indexes:
    "user_group_pkey" PRIMARY KEY, btree (id)
    "ux_user_group_owner_name" UNIQUE, btree (owner_user_id, lower(name))
Foreign-key constraints:
    "user_group_owner_user_id_fkey" FOREIGN KEY (owner_user_id) REFERENCES user_profile(id) ON DELETE CASCADE
Referenced by:
    TABLE "class_room" CONSTRAINT "class_room_class_id_fkey" FOREIGN KEY (class_id) REFERENCES user_group(id) ON DELETE CASCADE
    TABLE "resource_shares" CONSTRAINT "resource_shares_grantee_group_id_fkey" FOREIGN KEY (grantee_group_id) REFERENCES user_group(id) ON DELETE CASCADE
    TABLE "user_artifact" CONSTRAINT "user_artifact_group_id_fkey" FOREIGN KEY (group_id) REFERENCES user_group(id) ON DELETE SET NULL
    TABLE "user_group_member" CONSTRAINT "user_group_member_group_id_fkey" FOREIGN KEY (group_id) REFERENCES user_group(id) ON DELETE CASCADE
Triggers:
    trg_user_group_updated_at BEFORE UPDATE ON user_group FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap


\d+ public.user_group_member
                                        Table "public.user_group_member"
    Column     |  Type  | Collation | Nullable | Default  | Storage  | Compression | Stats target | Description 
---------------+--------+-----------+----------+----------+----------+-------------+--------------+-------------
 group_id      | uuid   |           | not null |          | plain    |             |              | 
 user_id       | uuid   |           | not null |          | plain    |             |              | 
 role_in_group | text   |           | not null |          | extended |             |              | 
 created_at    | bigint |           | not null | now_ms() | plain    |             |              | 
Indexes:
    "user_group_member_pkey" PRIMARY KEY, btree (group_id, user_id)
    "idx_user_group_member_user" btree (user_id)
Foreign-key constraints:
    "user_group_member_group_id_fkey" FOREIGN KEY (group_id) REFERENCES user_group(id) ON DELETE CASCADE
    "user_group_member_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
Access method: heap


\d+ public.user_identity
 Table "public.user_identity"
     Column     |  Type   | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
----------------+---------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id             | uuid    |           | not null | gen_random_uuid() | plain    |             |              | 
 user_id        | uuid    |           | not null |                   | plain    |             |              | 
 provider       | text    |           | not null |                   | extended |             |              | 
 subject        | text    |           | not null |                   | extended |             |              | 
 email          | citext  |           |          |                   | extended |             |              | 
 email_verified | boolean |           | not null | false             | plain    |             |              | 
 raw_profile    | jsonb   |           |          |                   | extended |             |              | 
 is_primary     | boolean |           | not null | false             | plain    |             |              | 
 connected_at   | bigint  |           | not null | now_ms()          | plain    |             |              | 
 last_login_at  | bigint  |           |          |                   | plain    |             |              | 
 created_at     | bigint  |           | not null | now_ms()          | plain    |             |              | 
 updated_at     | bigint  |           | not null | now_ms()          | plain    |             |              | 
Indexes:
    "user_identity_pkey" PRIMARY KEY, btree (id)
    "user_identity_provider_subject_key" UNIQUE CONSTRAINT, btree (provider, subject)
Foreign-key constraints:
    "user_identity_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
Triggers:
    trg_user_identity_updated_at BEFORE UPDATE ON user_identity FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap



\d+ public.user_memory
Table "public.user_memory"
   Column   |  Type  | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
------------+--------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id         | uuid   |           | not null | gen_random_uuid() | plain    |             |              | 
 user_id    | uuid   |           | not null |                   | plain    |             |              | 
 content    | text   |           | not null |                   | extended |             |              | 
 created_at | bigint |           | not null | now_ms()          | plain    |             |              | 
 updated_at | bigint |           | not null | now_ms()          | plain    |             |              | 
Indexes:
    "user_memory_pkey" PRIMARY KEY, btree (id)
Foreign-key constraints:
    "user_memory_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
Triggers:
    trg_user_memory_updated_at BEFORE UPDATE ON user_memory FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap



\d+ public.user_profile

                                                 Table "public.user_profile"
      Column       |  Type  | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
-------------------+--------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id                | uuid   |           | not null | gen_random_uuid() | plain    |             |              | 
 name              | text   |           |          |                   | extended |             |              | 
 email             | citext |           |          |                   | extended |             |              | 
 role              | text   |           |          |                   | extended |             |              | 
 profile_image_url | text   |           |          |                   | extended |             |              | 
 last_active_at    | bigint |           |          |                   | plain    |             |              | 
 created_at        | bigint |           | not null | now_ms()          | plain    |             |              | 
 updated_at        | bigint |           | not null | now_ms()          | plain    |             |              | 
 api_key           | text   |           |          |                   | extended |             |              | 
 settings          | jsonb  |           |          | '{}'::jsonb       | extended |             |              | 
 info              | jsonb  |           |          | '{}'::jsonb       | extended |             |              | 
 oauth_sub         | text   |           |          |                   | extended |             |              | 
Indexes:
    "user_profile_pkey" PRIMARY KEY, btree (id)
    "user_profile_api_key_key" UNIQUE CONSTRAINT, btree (api_key)
    "user_profile_oauth_sub_key" UNIQUE CONSTRAINT, btree (oauth_sub)
Referenced by:
    TABLE "class_assistant" CONSTRAINT "class_assistant_created_by_user_id_fkey" FOREIGN KEY (created_by_user_id) REFERENCES user_profile(id)
    TABLE "class_knowledge" CONSTRAINT "class_knowledge_created_by_user_id_fkey" FOREIGN KEY (created_by_user_id) REFERENCES user_profile(id)
    TABLE "class_message_reaction" CONSTRAINT "class_message_reaction_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
    TABLE "class_message" CONSTRAINT "class_message_target_user_id_fkey" FOREIGN KEY (target_user_id) REFERENCES user_profile(id) ON DELETE CASCADE
    TABLE "class_message" CONSTRAINT "class_message_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
    TABLE "class_read_receipt" CONSTRAINT "class_read_receipt_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
    TABLE "class_room" CONSTRAINT "class_room_created_by_user_id_fkey" FOREIGN KEY (created_by_user_id) REFERENCES user_profile(id)
    TABLE "class_room_member" CONSTRAINT "class_room_member_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
    TABLE "created_model" CONSTRAINT "created_model_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
    TABLE "created_prompt" CONSTRAINT "created_prompt_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
    TABLE "created_tool" CONSTRAINT "created_tool_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
    TABLE "library" CONSTRAINT "library_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
    TABLE "mcp_server" CONSTRAINT "mcp_server_owner_user_id_fkey" FOREIGN KEY (owner_user_id) REFERENCES user_profile(id) ON DELETE CASCADE
    TABLE "platform_capability_scope" CONSTRAINT "platform_capability_scope_created_by_fkey" FOREIGN KEY (created_by) REFERENCES user_profile(id) ON DELETE SET NULL
    TABLE "provider_credential" CONSTRAINT "provider_credential_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
    TABLE "resource_shares" CONSTRAINT "resource_shares_created_by_fkey" FOREIGN KEY (created_by) REFERENCES user_profile(id) ON DELETE CASCADE
    TABLE "resource_shares" CONSTRAINT "resource_shares_grantee_user_id_fkey" FOREIGN KEY (grantee_user_id) REFERENCES user_profile(id) ON DELETE CASCADE
    TABLE "user_artifact" CONSTRAINT "user_artifact_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
    TABLE "user_auth" CONSTRAINT "user_auth_id_fkey" FOREIGN KEY (id) REFERENCES user_profile(id) ON DELETE CASCADE
    TABLE "user_chat_tag" CONSTRAINT "user_chat_tag_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
    TABLE "user_chat" CONSTRAINT "user_chat_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
    TABLE "user_feedback" CONSTRAINT "user_feedback_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
    TABLE "user_file" CONSTRAINT "user_file_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
    TABLE "user_folder" CONSTRAINT "user_folder_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
    TABLE "user_group_member" CONSTRAINT "user_group_member_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
    TABLE "user_group" CONSTRAINT "user_group_owner_user_id_fkey" FOREIGN KEY (owner_user_id) REFERENCES user_profile(id) ON DELETE CASCADE
    TABLE "user_identity" CONSTRAINT "user_identity_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
    TABLE "user_memory" CONSTRAINT "user_memory_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
    TABLE "user_settings" CONSTRAINT "user_settings_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
    TABLE "user_tag" CONSTRAINT "user_tag_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
Triggers:
    trg_user_profile_updated_at BEFORE UPDATE ON user_profile FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap




\d+ public.user_settings
able "public.user_settings"
       Column        |          Type          | Collation | Nullable |                 Default                  | Storage  | Compression | Stats target | Description 
---------------------+------------------------+-----------+----------+------------------------------------------+----------+-------------+--------------+-------------
 user_id             | uuid                   |           | not null |                                          | plain    |             |              | 
 default_model       | character varying(100) |           | not null | 'gpt-oss:20B'::character varying         | extended |             |              | 
 default_temperature | double precision       |           | not null | 0.7                                      | plain    |             |              | 
 default_max_tokens  | integer                |           | not null | 500                                      | plain    |             |              | 
 embedding_model     | character varying(100) |           | not null | 'embeddinggemma:300m'::character varying | extended |             |              | 
 auto_save           | boolean                |           | not null | true                                     | plain    |             |              | 
 auto_save_interval  | integer                |           | not null | 30                                       | plain    |             |              | 
 theme               | character varying(20)  |           | not null | 'light'::character varying               | extended |             |              | 
 preferences         | jsonb                  |           |          | '{}'::jsonb                              | extended |             |              | 
 created_at          | bigint                 |           | not null | now_ms()                                 | plain    |             |              | 
 updated_at          | bigint                 |           | not null | now_ms()                                 | plain    |             |              | 
Indexes:
    "user_settings_pkey" PRIMARY KEY, btree (user_id)
Foreign-key constraints:
    "user_settings_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
Triggers:
    trg_user_settings_updated_at BEFORE UPDATE ON user_settings FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap


\d+ public.user_tag
  Table "public.user_tag"
 Column  | Type  | Collation | Nullable |   Default   | Storage  | Compression | Stats target | Description 
---------+-------+-----------+----------+-------------+----------+-------------+--------------+-------------
 id      | text  |           | not null |             | extended |             |              | 
 name    | text  |           | not null |             | extended |             |              | 
 user_id | uuid  |           | not null |             | plain    |             |              | 
 meta    | jsonb |           |          | '{}'::jsonb | extended |             |              | 
Indexes:
    "user_tag_pkey" PRIMARY KEY, btree (id, user_id)
Foreign-key constraints:
    "user_tag_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
Access method: heap


