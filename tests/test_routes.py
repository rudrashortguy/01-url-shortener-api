"""Integration tests for API routes via TestClient."""

from __future__ import annotations

import pytest


class TestCreateUrl:
    """POST /api/v1/urls tests."""

    def test_create_url(self, client):
        resp = client.post(
            "/api/v1/urls",
            json={"original_url": "https://example.com"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["short_code"]
        assert len(data["short_code"]) >= 6
        assert data["original_url"] == "https://example.com"
        assert data["endpoint"] == f"/r/{data['short_code']}"

    def test_create_with_custom_slug(self, client):
        resp = client.post(
            "/api/v1/urls",
            json={"original_url": "https://example.com", "custom_slug": "mylink"},
        )
        assert resp.status_code == 201
        assert resp.json()["short_code"] == "mylink"

    def test_create_collision(self, client):
        client.post(
            "/api/v1/urls",
            json={"original_url": "https://example.com", "custom_slug": "taken"},
        )
        resp = client.post(
            "/api/v1/urls",
            json={"original_url": "https://other.com", "custom_slug": "taken"},
        )
        assert resp.status_code == 409

    def test_create_invalid_url(self, client):
        resp = client.post(
            "/api/v1/urls",
            json={"original_url": "not-a-url"},
        )
        assert resp.status_code == 422

    def test_create_custom_slug_too_short(self, client):
        resp = client.post(
            "/api/v1/urls",
            json={"original_url": "https://example.com", "custom_slug": "ab"},
        )
        assert resp.status_code == 422


class TestResolveUrl:
    """GET /api/v1/urls/r/{slug} tests."""

    def _create(self, client, slug: str = "testres"):
        client.post(
            "/api/v1/urls",
            json={
                "original_url": "https://example.com",
                "custom_slug": slug,
            },
        )

    def test_redirect(self, client):
        self._create(client)
        resp = client.get("/api/v1/urls/r/testres")
        assert resp.status_code == 301
        assert resp.headers["location"] == "https://example.com"

    def test_json_response(self, client):
        self._create(client)
        resp = client.get(
            "/api/v1/urls/r/testres",
            headers={"Accept": "application/json"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["original_url"] == "https://example.com"
        assert data["clicks"] >= 1

    def test_not_found(self, client):
        resp = client.get("/api/v1/urls/r/nonexistent")
        assert resp.status_code == 404


class TestStats:
    """GET /api/v1/urls/r/{slug}/stats tests."""

    def test_stats(self, client):
        client.post(
            "/api/v1/urls",
            json={"original_url": "https://example.com", "custom_slug": "st"},
        )
        resp = client.get("/api/v1/urls/r/st/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["short_code"] == "st"
        assert isinstance(data["clicks"], int)

    def test_stats_not_found(self, client):
        resp = client.get("/api/v1/urls/r/nope/stats")
        assert resp.status_code == 404


class TestDelete:
    """DELETE /api/v1/urls/r/{slug} tests."""

    def test_delete_success(self, client):
        client.post(
            "/api/v1/urls",
            json={"original_url": "https://example.com", "custom_slug": "todelete"},
        )
        resp = client.delete("/api/v1/urls/r/todelete")
        assert resp.status_code == 204

    def test_delete_not_found(self, client):
        resp = client.delete("/api/v1/urls/r/nosuchthing")
        assert resp.status_code == 404


class TestHealth:
    """Health check endpoint."""

    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"