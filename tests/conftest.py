"""Shared pytest fixtures."""

from __future__ import annotations

from typing import Generator

import pytest
import redis
from fastapi.testclient import TestClient

import sys
import os

# Add src to path so tests can import the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from main import app
from dependencies import get_redis
from services.url_service import UrlService


@pytest.fixture(scope="session")
def redis_client() -> Generator[redis.Redis[str], None, None]:
    """Use the real Redis from the environment or a test container."""
    url = os.environ.get("REDIS_URL", "redis://localhost:6379/9")
    r = redis.Redis.from_url(url, decode_responses=True)
    try:
        r.ping()
    except redis.ConnectionError as exc:
        pytest.skip(f"Redis not available at {url}: {exc}")
    # Flush test db to avoid leaking between runs
    r.flushdb()
    yield r
    r.flushdb()
    r.close()


@pytest.fixture
def svc(redis_client: redis.Redis[str]) -> UrlService:
    return UrlService(redis_client)


@pytest.fixture
def client(svc: UrlService, redis_client: redis.Redis[str]):
    """Test client with app.state.redis set up."""
    app.state.redis = redis_client

    def _override():
        return redis_client

    app.dependency_overrides[get_redis] = _override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()