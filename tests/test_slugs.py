"""Tests for slug generation utilities."""

from __future__ import annotations

import string

from utils.slugs import generate_slug, is_valid_slug, slug_from_uuid, _encode_base62


class TestGenerateSlug:
    """Slug generation tests."""

    def test_deterministic_with_seed(self):
        """Same seed produces same slug."""
        s1 = generate_slug(seed=42)
        s2 = generate_slug(seed=42)
        assert s1 == s2

    def test_default_has_min_length(self):
        """Random slugs are at least 6 characters."""
        slug = generate_slug()
        assert len(slug) >= 6

    def test_custom_length(self):
        """Min length parameter works."""
        slug = generate_slug(seed=1, min_length=10)
        assert len(slug) >= 10

    def test_randomness(self):
        """Different seeds produce different slugs (usually)."""
        slugs = {generate_slug(seed=i) for i in range(100)}
        # With 62^6 possible values, collisions in 100 trials are astronomically
        # unlikely; if they occur we just want >1 unique slug.
        assert len(slugs) > 1


class TestIsValidSlug:
    """Slug validation tests."""

    def test_valid_alphanumeric(self):
        assert is_valid_slug("aB3xYz") is True

    def test_too_short(self):
        assert is_valid_slug("abc") is False

    def test_empty(self):
        assert is_valid_slug("") is False

    def test_contains_special_chars(self):
        assert is_valid_slug("hello!world") is False

    def test_numbers_only(self):
        assert is_valid_slug("123456") is True


class TestEncodeBase62:
    """Base62 encoding edge cases."""

    def test_zero(self):
        assert _encode_base62(0) == "a"

    def test_small_numbers(self):
        assert _encode_base62(1) == "b"

    def test_exact_base(self):
        # 62 -> should produce "a" + one more char (since alphabet starts at 'a'=0)
        result = _encode_base62(62)
        assert len(result) == 2


class TestSlugFromUUID:
    """UUID-derived slug tests."""

    def test_deterministic(self):
        uuid = "550e8400-e29b-41d4-a716-446655440000"
        s1 = slug_from_uuid(uuid)
        s2 = slug_from_uuid(uuid)
        assert s1 == s2

    def test_produces_valid_slug(self):
        uuid = "00000000-0000-0000-0000-000000000001"
        slug = slug_from_uuid(uuid)
        assert is_valid_slug(slug)