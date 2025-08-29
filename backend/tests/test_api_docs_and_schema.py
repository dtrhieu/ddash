from __future__ import annotations

from rest_framework.test import APIClient


def test_schema_lite_and_docs_accessible():
    client = APIClient()

    # /api/schema-lite returns JSON with endpoints list and count >= minimal expected
    r = client.get("/api/schema-lite")
    assert r.status_code == 200, (r.status_code, r.content[:200])
    data = r.json()
    assert isinstance(data, dict)
    assert "endpoints" in data and isinstance(data["endpoints"], list), data
    assert data.get("count", 0) >= 5, data

    # /api/docs/ renders HTML page that mentions DDash API
    r2 = client.get("/api/docs/")
    assert r2.status_code == 200, (r2.status_code, r2.content[:200])
    assert b"DDash API" in r2.content
