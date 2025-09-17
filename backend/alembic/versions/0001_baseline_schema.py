# backend/alembic/versions/0001_baseline_schema.py
"""Baseline schema from consolidated SQL + patches (DDL-first).
"""
from __future__ import annotations
from pathlib import Path
from alembic import op

# revision identifiers, used by Alembic.
revision = "0001_baseline_schema"
down_revision = None
branch_labels = None
depends_on = None

def _read_if_exists(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""

def upgrade() -> None:
    # Create required extensions & helpers up front (idempotent in SQL files is fine).
    # Prefer running your canonical consolidated SQL first, then additive patches.
    root = Path(".")
    # Try both naming variants for the consolidated file
    consolidated = None
    for p in [
        root / "db" / "database_schema_consolidated_v2.sql",
        root / "db" / "database_schema_consolidated.sql",
    ]:
        if p.exists():
            consolidated = p
            break
    if not consolidated:
        raise RuntimeError("Consolidated SQL not found under db/. Expected database_schema_consolidated_v2.sql or database_schema_consolidated.sql")

    op.execute(_read_if_exists(consolidated))

    # Patches in order (if present)
    for fname in [
        "patch_add_mcp.sql",
        "patch_add_platform_capabilities.sql",
        "patch_add_indexes.sql",
    ]:
        f = root / "db" / fname
        if f.exists():
            op.execute(_read_if_exists(f))

def downgrade() -> None:
    # Intentionally empty: we do not attempt destructive downgrades.
    # If you need a rollback, create a dedicated down migration.
    pass

