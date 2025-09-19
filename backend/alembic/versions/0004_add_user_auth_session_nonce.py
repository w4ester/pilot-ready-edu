"""Add per-user session nonce for revocable sessions."""

from alembic import op


revision = "0004_add_user_auth_session_nonce"
down_revision = "0003_align_embedding_dimension"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE user_auth
          ADD COLUMN IF NOT EXISTS session_nonce TEXT;

        UPDATE user_auth
          SET session_nonce = encode(gen_random_bytes(16), 'hex')
        WHERE session_nonce IS NULL;

        ALTER TABLE user_auth
          ALTER COLUMN session_nonce SET NOT NULL;

        ALTER TABLE user_auth
          ALTER COLUMN session_nonce SET DEFAULT encode(gen_random_bytes(16), 'hex');
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE user_auth
          DROP COLUMN IF EXISTS session_nonce;
        """
    )
