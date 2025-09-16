"""FastAPI application entry point."""

from fastapi import FastAPI

from .api import api_router
from .core.settings import get_settings

settings = get_settings()

app = FastAPI(
    title="Edinfinite Platform API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.on_event("startup")
async def startup_event() -> None:  # pragma: no cover - placeholder for future hooks
    _ = settings


app.include_router(api_router)
