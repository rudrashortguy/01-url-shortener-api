"""Tests for the UrlService layer."""

from __future__ import annotations

import datetime

import pytest

from services.url_service import UrlService


class TestUrlService:
    """Service unit tests against Redis."""

    def test_create_and_get(self, svc: UrlService):
        record = svc.create("https://example.com", custom_slug="test01")
        assert record.slug == "test01"
        assert record.original_url == "https://example.com"
        assert record.clicks == 0
        assert record.created_at  # non-empty

        fetched = svc.get("test01")
        assert fetched is not None
        assert fetched.original_url == "https://example.com"

    def test_create_returns_new_slug_when_no_custom(self, svc: UrlService):
        record = svc.create("https://example.org")
        assert record.slug
        assert len(record.slug) >= 6
        fetched = svc.get(record.slug)
        assert fetched is not None
        assert fetched.original_url == "https://example.org"

    def test_create_with_expiry(self, svc: UrlService):
        record = svc.create(
            "https://example.com",
            expires_in_seconds=3600,
            custom_slug="temp",
        )
        assert record.expires_at is not None
        fetched = svc.get("temp")
        assert fetched.expires_at is not None

    def test_delete(self, svc: UrlService):
        svc.create("https://example.com", custom_slug="delme")
        assert svc.delete("delme") is True
        assert svc.get("delme") is None

    def test_delete_missing(self, svc: UrlService):
        assert svc.delete("nonexistent") is False

    def test_increment_clicks(self, svc: UrlService):
        svc.create("https://example.com", custom_slug="clicks")
        count = svc.increment_clicks("clicks")
        assert count == 1
        count2 = svc.increment_clicks("clicks")
        assert count2 == 2

    def test_stats_returns_record(self, svc: UrlService):
        svc.create("https://example.com", custom_slug="statstest")
        svc.increment_clicks("statstest")
        record = svc.stats("statstest")
        assert record is not None
        assert record.clicks == 1

    def test_collision_error_on_duplicate_custom_slug(self, svc: UrlService):
        svc.create("https://example.com", custom_slug="dupe")
        with pytest.raises(ValueError, match="already taken"):
            svc.create("https://other.com", custom_slug="dupe")

    def test_invalid_custom_slug_format(self, svc: UrlService):
        with pytest.raises(ValueError, match="alphanumeric"):
            svc.create("https://example.com", custom_slug="ab")  # too short

    def test_get_missing_returns_none(self, svc: UrlService):
        assert svc.get("zzzzzzmissing") is None