"""Set document_chunk embedding to vector(768) with HNSW."""

from alembic import op


revision = "0002_vector_768_hnsw"
down_revision = "0001_baseline_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS idx_document_chunk_embedding;
        DROP INDEX IF EXISTS idx_document_chunk_embedding_hnsw;
        DROP INDEX IF EXISTS idx_document_chunk_tsv_gin;

        ALTER TABLE document_chunk
          ALTER COLUMN embedding TYPE vector(768);

        CREATE INDEX IF NOT EXISTS idx_document_chunk_embedding_hnsw
          ON document_chunk USING hnsw (embedding vector_cosine_ops);

        CREATE INDEX IF NOT EXISTS idx_document_chunk_tsv_gin
          ON document_chunk USING gin (content_tsv);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS idx_document_chunk_embedding_hnsw;
        DROP INDEX IF EXISTS idx_document_chunk_tsv_gin;

        ALTER TABLE document_chunk
          ALTER COLUMN embedding TYPE vector(1536);

        CREATE INDEX IF NOT EXISTS idx_document_chunk_embedding
          ON document_chunk USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

        CREATE INDEX IF NOT EXISTS idx_document_chunk_tsv_gin
          ON document_chunk USING gin (content_tsv);
        """
    )

