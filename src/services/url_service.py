"""Core URL shortener service.

Handles create, resolve, stats, and delete operations against Redis.
"""

from __future__ import annotations

import datetime
from dataclasses import asdict, dataclass
from typing import Any

import redis


@dataclass
class UrlRecord:
    """Serialized representation of a shortened URL stored in Redis."""

    original_url: str
    slug: str
    created_at: str
    expires_at: str | None
    clicks: int = 0


class UrlService:
    """Redis-backed URL shortener service."""

    def __init__(self, r: redis.Redis[str]) -> None:
        self._r = r
        # Counter key used for deterministic slug generation.
        self._counter_key = "url_counter"

    # ── create ───────────────────────────────────────────────────────────

    def create(
        self,
        original_url: str,
        *,
        custom_slug: str | None = None,
        expires_in_seconds: int | None = None,
    ) -> UrlRecord:
        """Store a new URL and return its record.

        Raises:
            ValueError: if the custom_slug is already taken.
        """
        if custom_slug:
            if not _is_valid_slug_format(custom_slug):
                raise ValueError("custom_slug must be at least 4 alphanumeric characters")
            if self._r.exists(f"url:{custom_slug}"):
                raise ValueError(f"Slug '{custom_slug}' is already taken")
            slug = custom_slug
        else:
            slug = self._generate_slug()

        expires_at = (
            (
                datetime.datetime.now(datetime.timezone.utc)
                + datetime.timedelta(seconds=expires_in_seconds)
            ).isoformat()
            if expires_in_seconds
            else None
        )
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()

        record = UrlRecord(
            original_url=original_url,
            slug=slug,
            created_at=now,
            expires_at=expires_at,
        )
        payload = self._serialize(record)
        self._r.set(f"url:{slug}", payload)
        if expires_in_seconds:
            self._r.expire(f"url:{slug}", expires_in_seconds)
        return record

    # ── resolve ──────────────────────────────────────────────────────────

    def get(self, slug: str) -> UrlRecord | None:
        """Return the UrlRecord for a slug, or None if missing/expired."""
        raw = self._r.get(f"url:{slug}")
        if not raw:
            return None
        return self._deserialize(raw)

    def increment_clicks(self, slug: str) -> int | None:
        """Atomically bump the click counter. Returns new count or None."""
        data = self._r.get(f"url:{slug}")
        if not data:
            return None
        record = self._deserialize(data)
        record.clicks += 1
        self._r.set(f"url:{slug}", self._serialize(record))
        return record.clicks

    # ── stats ────────────────────────────────────────────────────────────

    def stats(self, slug: str) -> UrlRecord | None:
        """Return the full record (click count, timestamps, etc.)."""
        return self.get(slug)

    # ── delete ───────────────────────────────────────────────────────────

    def delete(self, slug: str) -> bool:
        """Remove a short URL. Returns True if it existed."""
        return bool(self._r.delete(f"url:{slug}"))

    # ── private helpers ──────────────────────────────────────────────────

    def _generate_slug(self) -> str:
        """Generate a new slug using an atomic Redis counter."""
        counter = self._r.incr(self._counter_key)
        from ..utils.slugs import generate_slug

        return generate_slug(int(counter), min_length=6)

    @staticmethod
    def _serialize(record: UrlRecord) -> bytes:
        return ",".join(
            [
                record.original_url,
                record.created_at,
                record.expires_at or "",
                str(record.clicks),
            ]
        ).encode()

    @staticmethod
    def _deserialize(raw: bytes | str) -> UrlRecord:
        if isinstance(raw, bytes):
            parts = raw.decode().split(",", 3)
        else:
            parts = raw.split(",", 3)
        return UrlRecord(
            original_url=parts[0],
            slug="",  # resolved later via key lookup
            created_at=parts[1],
            expires_at=parts[2] or None,
            clicks=int(parts[3]),
        )


def _is_valid_slug_format(slug: str) -> bool:
    if len(slug) < 4:
        return False
    return slug.isalnum()