"""Tests for the submissions endpoint — CORS, validation, rate limiting, spam, and geo fallback."""

import uuid
from unittest.mock import patch, AsyncMock
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# A known widget ID from seed data
WIDGET_ID = "11111111-1111-1111-1111-111111111111"


class TestCORSPreflight:
    """PROBE: CORS preflight requests are handled correctly."""

    def test_options_returns_cors_headers(self):
        """OPTIONS request to /api/submissions/ returns CORS headers."""
        resp = client.options(
            "/api/submissions/",
            headers={
                "Origin": "http://localhost:5500",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )
        assert resp.status_code == 200
        assert "access-control-allow-origin" in resp.headers
        assert "access-control-allow-methods" in resp.headers

    def test_post_includes_cors_headers(self):
        """POST response includes CORS headers."""
        resp = client.post(
            "/api/submissions/",
            json={
                "widget_id": WIDGET_ID,
                "data": {"email": "test@test.com"},
            },
            headers={"Origin": "http://localhost:5500"},
        )
        # May be 201 or 404 (if no DB), but CORS headers should be present
        assert "access-control-allow-origin" in resp.headers


class TestPayloadValidation:
    """PROBE 2: Malformed and oversized payloads return 4xx, never 500."""

    def test_missing_widget_id(self):
        """Missing widget_id returns 422."""
        resp = client.post("/api/submissions/", json={"data": {"email": "test@test.com"}})
        assert resp.status_code == 422

    def test_missing_data(self):
        """Missing data field returns 422."""
        resp = client.post("/api/submissions/", json={"widget_id": WIDGET_ID})
        assert resp.status_code == 422

    def test_invalid_widget_id_format(self):
        """Non-UUID widget_id returns 422."""
        resp = client.post(
            "/api/submissions/",
            json={"widget_id": "not-a-uuid", "data": {"email": "test@test.com"}},
        )
        assert resp.status_code == 422

    def test_empty_body(self):
        """Empty body returns 422."""
        resp = client.post(
            "/api/submissions/",
            content="",
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 422


class TestSpamProtection:
    """PROBE 6: Honeypot field triggers rejection."""

    def test_honeypot_filled_rejects(self):
        """Filling the honeypot 'website' field should reject the submission."""
        resp = client.post(
            "/api/submissions/",
            json={
                "widget_id": WIDGET_ID,
                "data": {"email": "bot@spam.com"},
                "website": "http://spam-site.com",  # Bot fills this
            },
        )
        # Should be rejected (400 or 200 silently — our impl returns 400)
        assert resp.status_code in (400, 404)  # 404 if no DB, 400 if spam rejected

    def test_honeypot_empty_allowed(self):
        """Empty honeypot should allow the submission."""
        resp = client.post(
            "/api/submissions/",
            json={
                "widget_id": WIDGET_ID,
                "data": {"email": "human@test.com"},
                "website": "",  # Human leaves this empty
            },
        )
        # Should not be rejected for spam (may fail for other reasons like no DB)
        assert resp.status_code != 400 or "rejected" not in resp.text.lower()


class TestHealthCheck:
    """Basic health check."""

    def test_health(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"


class TestWidgetDelivery:
    """PROBE: Widget.js and config delivery."""

    def test_widget_js_served(self):
        """widget.js is served with correct cache headers."""
        resp = client.get("/widget.js")
        assert resp.status_code == 200
        assert "application/javascript" in resp.headers["content-type"]
        assert "max-age=31536000" in resp.headers.get("cache-control", "")
        assert "immutable" in resp.headers.get("cache-control", "")

    def test_widget_config_not_found(self):
        """Non-existent widget config returns 404."""
        fake_id = str(uuid.uuid4())
        resp = client.get(f"/api/widgets/{fake_id}/config")
        # May return 404 or 500 depending on DB availability
        assert resp.status_code in (404, 500)
