"""Align document_chunk embedding vector dimension with runtime model."""

from alembic import op


revision = "0003_align_embedding_dimension"
down_revision = "0002_vector_768_hnsw"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS idx_document_chunk_embedding;
        DROP INDEX IF EXISTS idx_document_chunk_embedding_hnsw;

        ALTER TABLE document_chunk
          ALTER COLUMN embedding TYPE vector(768);

        CREATE INDEX IF NOT EXISTS idx_document_chunk_embedding_hnsw
          ON document_chunk USING hnsw (embedding vector_cosine_ops);

        ANALYZE document_chunk;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS idx_document_chunk_embedding_hnsw;

        ALTER TABLE document_chunk
          ALTER COLUMN embedding TYPE vector(1536);

        CREATE INDEX IF NOT EXISTS idx_document_chunk_embedding
          ON document_chunk USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

        ANALYZE document_chunk;
        """
    )
