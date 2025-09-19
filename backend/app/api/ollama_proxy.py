"""Proxy requests to the Ollama service so it stays private."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, Response, status
import httpx

from ..core.settings import get_settings


router = APIRouter(prefix="/api/v1/ollama", tags=["ollama"])


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy_ollama(path: str, request: Request) -> Response:
    """Forward arbitrary requests to the configured Ollama host."""

    settings = get_settings()
    upstream = settings.ollama_host.rstrip("/")
    target_url = f"{upstream}/api/{path}" if path else f"{upstream}/api"

    try:
        async with httpx.AsyncClient(timeout=None) as client:
            upstream_response = await client.request(
                request.method,
                target_url,
                headers={
                    k: v
                    for k, v in request.headers.items()
                    if k.lower() not in {"host", "content-length"}
                },
                params=dict(request.query_params),
                content=await request.body(),
            )
    except httpx.HTTPError as exc:  # pragma: no cover - network failure path
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="ollama_upstream_error",
        ) from exc

    # Propagate key headers while avoiding hop-by-hop ones.
    headers = {}
    for key, value in upstream_response.headers.items():
        lower = key.lower()
        if lower in {"content-type", "content-length", "content-encoding"}:
            headers[key] = value

    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=headers,
    )
