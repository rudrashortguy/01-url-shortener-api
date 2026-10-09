"""Shared FastAPI dependencies."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import redis
from fastapi import Request
from starlette.responses import JSONResponse

from .config import settings


async def get_redis(request: Request) -> redis.Redis[str]:
    """Yield a Redis connection from the app state."""
    state = request.app.state
    if not hasattr(state, "redis"):
        state.redis = redis.Redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=2,
        )
    return state.redis


@asynccontextmanager
async def lifespan(app):
    """Lifespan: open Redis on startup, close on shutdown."""
    app.state.redis = redis.Redis.from_url(
        settings.redis_url,
        decode_responses=True,
        socket_connect_timeout=2,
    )
    yield
    app.state.redis.close()