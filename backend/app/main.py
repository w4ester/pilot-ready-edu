"""FastAPI application entry point."""

from fastapi import FastAPI

from .core.settings import get_settings
from .routers import api_router

settings = get_settings()

app = FastAPI(
    title="Edinfinite Platform API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.on_event("startup")
async def startup_event() -> None:
    # Future startup hooks (database warm-up, telemetry, etc.) go here.
    _ = settings


app.include_router(api_router)
