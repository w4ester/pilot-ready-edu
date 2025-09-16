"""Health endpoints."""

import os
from datetime import datetime

from fastapi import APIRouter

router = APIRouter()


@router.get("/schema", summary="Return Alembic head revision")
def schema_health() -> dict[str, str | None]:
    """Return alembic head revision information for observability checks."""

    head = os.getenv("ALEMBIC_HEAD") or os.getenv("ALEMBIC_REVISION")
    return {
        "status": "ok",
        "head": head or "unknown",
        "checked_at": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/live", summary="Liveness probe")
def live() -> dict[str, str]:
    """Simple liveness endpoint for container orchestration."""

    return {"status": "alive"}
