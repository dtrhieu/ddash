#!/usr/bin/env python3
"""
Smoke test for M2.6 API documentation endpoints.
- Verifies /api/schema returns JSON with paths
- Verifies /api/docs/ returns HTML page (200 OK)

Usage:
  python3 scripts/smoke_m26.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
sys.path.insert(0, str(ROOT / "backend"))

import django  # noqa: E402

django.setup()

from rest_framework.test import APIClient  # noqa: E402


if __name__ == "__main__":
    client = APIClient()
    # schema-lite
    r = client.get("/api/schema-lite")
    assert r.status_code == 200, (r.status_code, r.content[:200])
    data = r.json()
    assert (
        "endpoints" in data
        and isinstance(data["endpoints"], list)
        and data["count"] >= 5
    ), data
    # docs
    r2 = client.get("/api/docs/")
    assert r2.status_code == 200, (r2.status_code, r2.content[:200])
    assert b"DDash API" in r2.content
    print("M2.6 smoke test passed.")
