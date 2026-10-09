"""Seed demo data into the URL shortener.

Usage:
    python scripts/seed.py
"""

from __future__ import annotations

import os
import sys

import redis

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from services.url_service import UrlService


DEMO_URLS = [
    ("https://github.com", "gh"),
    ("https://docs.python.org/3/", "pydoc"),
    ("https://fastapi.tiangolo.com/", "fastapi"),
    ("https://redis.io/docs/", "redis"),
    ("https://pytest.org/", "pytest"),
]


def main() -> None:
    url = os.environ.get("URLSHORTENER_REDIS_URL", "redis://localhost:6379/0")
    r = redis.Redis.from_url(url, decode_responses=True)
    r.ping()
    r.flushdb()

    svc = UrlService(r)
    print("Seeding demo URLs...")
    for original, slug in DEMO_URLS:
        svc.create(original, custom_slug=slug)
        print(f"  {slug} -> {original}")
    print(f"\nDone. Visit http://localhost:8000/docs for the OpenAPI spec.")


if __name__ == "__main__":
    main()