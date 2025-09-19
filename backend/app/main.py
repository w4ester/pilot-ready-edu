"""FastAPI application entry point."""

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

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


app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret_key,
    session_cookie=settings.session_cookie_name,
    https_only=settings.session_cookie_secure,
    same_site=settings.session_cookie_samesite,
    max_age=settings.session_max_age_seconds,
    domain=settings.session_cookie_domain,
)


app.include_router(api_router)
