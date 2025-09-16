-- patch_add_indexes.sql
BEGIN;

-- User chats: filter active threads by owner and recency
CREATE INDEX IF NOT EXISTS idx_user_chat_user_updated
  ON user_chat (user_id, updated_at DESC)
  WHERE archived = false;

CREATE INDEX IF NOT EXISTS idx_user_chat_user_pinned
  ON user_chat (user_id, pinned, updated_at DESC)
  WHERE archived = false AND pinned = true;

-- Class messages: room timeline, author lookups, threaded replies
CREATE INDEX IF NOT EXISTS idx_class_message_room_created
  ON class_message (class_room_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_class_message_user
  ON class_message (user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_class_message_parent
  ON class_message (parent_id, created_at)
  WHERE parent_id IS NOT NULL;

-- Group membership lookups by user
CREATE INDEX IF NOT EXISTS idx_user_group_member_user
  ON user_group_member (user_id);

COMMIT;
