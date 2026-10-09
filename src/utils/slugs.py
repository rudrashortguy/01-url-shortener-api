"""Base62 slug generation for short URLs.

Generates collision-resistant, SEO-friendly short codes from a counter or
UUID. Uses a deterministic base62 alphabet (a-zA-Z0-9) so slugs are URL-safe
and look natural.
"""

from __future__ import annotations

import secrets
import string

# Deterministic alphabet: a-z A-Z 0-9
_ALPHABET: str = string.ascii_lowercase + string.ascii_uppercase + string.digits
_BASE: int = len(_ALPHABET)
_MIN_LENGTH: int = 6


def _encode_base62(n: int) -> str:
    """Encode a non-negative integer in base62."""
    if n == 0:
        return _ALPHABET[0]
    chars: list[str] = []
    while n:
        n, rem = divmod(n, _BASE)
        chars.append(_ALPHABET[rem])
    return "".join(reversed(chars))


def _pad_left(value: str, width: int) -> str:
    """Pad a base62 string to at least `width` characters."""
    if len(value) >= width:
        return value
    return _ALPHABET[0] * (width - len(value)) + value


def generate_slug(seed: int | None = None, min_length: int = _MIN_LENGTH) -> str:
    """Generate a short, URL-safe slug.

    Args:
        seed: Optional integer seed. When provided, the slug is fully
            deterministic for the same seed, which is handy for tests.
        min_length: Minimum number of characters the slug should have.

    Returns:
        A base62 string of at least `min_length` characters.
    """
    if seed is None:
        # Use a random 64-bit integer to avoid sequential slugs in production.
        seed = secrets.randbits(64)
    encoded = _encode_base62(seed)
    return _pad_left(encoded, min_length)


def slug_from_uuid(uuid_str: str, min_length: int = _MIN_LENGTH) -> str:
    """Derive a slug from a UUID string (deterministic)."""
    # Strip hyphens and treat as a big hex number.
    cleaned = uuid_str.replace("-", "")
    value = int(cleaned, 16)
    return _pad_left(_encode_base62(value), min_length)


def is_valid_slug(slug: str, min_length: int = _MIN_LENGTH) -> bool:
    """Return True if `slug` is a valid short code."""
    if not slug or len(slug) < min_length:
        return False
    allowed = set(_ALPHABET)
    return all(c in allowed for c in slug)