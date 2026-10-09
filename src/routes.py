"""URL shortener API routes."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi import status as http_status
from redis import Redis, RedisError

from .models import CreateUrlRequest, CreateUrlResponse, StatsResponse
from .services.url_service import UrlService

router = APIRouter(prefix="/urls", tags=["urls"])


def _get_service(req: Request) -> UrlService:
    r: Redis[str] = req.app.state.redis
    return UrlService(r)


def _parse_dt(s: str) -> datetime:
    """Parse an ISO-8601 timestamp string into a timezone-aware datetime."""
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


@router.post("", response_model=CreateUrlResponse, status_code=201)
async def create_url(
    body: CreateUrlRequest,
    req: Request,
) -> CreateUrlResponse:
    """Shorten a URL."""
    try:
        svc = _get_service(req)
        record = svc.create(
            str(body.original_url),
            custom_slug=body.custom_slug,
            expires_in_seconds=body.expires_in_seconds,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except RedisError as exc:
        raise HTTPException(status_code=503, detail="Redis unavailable") from exc

    return CreateUrlResponse(
        short_code=record.slug,
        short_url=f"{req.base_url}/r/{record.slug}",
        original_url=record.original_url,
        created_at=_parse_dt(record.created_at),
        expires_at=_parse_dt(record.expires_at) if record.expires_at else None,
        endpoint=f"/r/{record.slug}",
    )


@router.get("/r/{short_code}")
async def resolve_url(
    short_code: str,
    req: Request,
    response: Response,
):
    """Resolve a short code to the original URL.

    Supports `Accept: application/json` to return JSON instead of redirecting.
    """
    try:
        svc = _get_service(req)
        record = svc.get(short_code)
    except RedisError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis unavailable",
        ) from exc

    if not record:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Short URL not found",
        )

    # Increment click counter
    svc.increment_clicks(short_code)

    if req.headers.get("accept", "").startswith("application/json"):
        return {
            "short_code": short_code,
            "original_url": record.original_url,
            "clicks": record.clicks,
        }

    response.headers["X-Original-Url"] = record.original_url
    response.headers["X-Clicks"] = str(record.clicks)
    return Response(
        status_code=http_status.HTTP_301_MOVED_PERMANENTLY,
        headers={"Location": record.original_url},
    )


@router.get("/r/{short_code}/stats", response_model=StatsResponse)
async def get_stats(
    short_code: str,
    req: Request,
) -> StatsResponse:
    """Return analytics for a short code."""
    try:
        svc = _get_service(req)
        record = svc.stats(short_code)
    except RedisError as exc:
        raise HTTPException(status_code=503, detail="Redis unavailable") from exc

    if not record:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return StatsResponse(
        short_code=record.slug,
        original_url=record.original_url,
        created_at=_parse_dt(record.created_at),
        clicks=record.clicks,
        expires_at=_parse_dt(record.expires_at) if record.expires_at else None,
    )


@router.delete("/r/{short_code}", status_code=204)
async def delete_url(
    short_code: str,
    req: Request,
) -> None:
    """Delete a short URL."""
    try:
        svc = _get_service(req)
        deleted = svc.delete(short_code)
    except RedisError as exc:
        raise HTTPException(status_code=503, detail="Redis unavailable") from exc

    if not deleted:
        raise HTTPException(status_code=404, detail="Short URL not found")