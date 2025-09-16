"""Health endpoints for monitoring and smoke tests."""

from datetime import datetime
import os

from fastapi import APIRouter

router = APIRouter()


@router.get("/schema", summary="Return Alembic head revision")
def schema_health() -> dict[str, str | None]:
    head = os.getenv("ALEMBIC_HEAD") or os.getenv("ALEMBIC_REVISION")
    return {
        "status": "ok",
        "head": head or "unknown",
        "checked_at": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/live", summary="Simple liveness probe")
def live() -> dict[str, str]:
    return {"status": "alive"}
