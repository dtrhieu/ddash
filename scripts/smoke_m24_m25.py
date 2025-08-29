#!/usr/bin/env python3
"""
Smoke test for M2.4 (URL routing) and M2.5 (fixtures + endpoints).
- Sets up Django
- Loads fixtures (core + scheduling)
- Uses DRF APIClient to hit list endpoints
- Exercises CRUD on a simple entity (Field)

Usage:
  python3 scripts/smoke_m24_m25.py -v
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
sys.path.insert(0, str(ROOT / "backend"))

import django  # noqa: E402

django.setup()

from django.core import management  # noqa: E402
from rest_framework.test import APIClient  # noqa: E402


FIXTURES = [
    str(ROOT / "backend/core/fixtures/initial_core.json"),
    str(ROOT / "backend/scheduling/fixtures/initial_scheduling.json"),
]


def load_fixtures(verbose: bool = False) -> None:
    for f in FIXTURES:
        if not Path(f).exists():
            raise SystemExit(f"Missing fixture: {f}")
    management.call_command("flush", verbosity=0, interactive=False)
    management.call_command("loaddata", *FIXTURES, verbosity=1 if verbose else 0)


def list_endpoints(client: APIClient, endpoints: Iterable[str]) -> None:
    for ep in endpoints:
        resp = client.get(ep)
        assert (
            resp.status_code == 200
        ), f"GET {ep} expected 200, got {resp.status_code}, body={resp.content!r}"
        data = resp.json()
        assert "results" in data or isinstance(
            data, list
        ), f"Unexpected payload for {ep}: {data}"


def crud_field(client: APIClient) -> None:
    # Create
    resp = client.post("/api/fields/", {"name": "Gamma"}, format="json")
    assert resp.status_code == 201, (resp.status_code, resp.content)
    fid = resp.json()["id"]
    # Retrieve
    resp = client.get(f"/api/fields/{fid}/")
    assert resp.status_code == 200
    # Update
    resp = client.patch(f"/api/fields/{fid}/", {"name": "Gamma-Updated"}, format="json")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Gamma-Updated"
    # Delete
    resp = client.delete(f"/api/fields/{fid}/")
    assert resp.status_code == 204


if __name__ == "__main__":
    verbose = "-v" in sys.argv or "--verbose" in sys.argv
    load_fixtures(verbose=verbose)

    client = APIClient()
    # No auth for now (M2 phase), public endpoints

    # Basic list tests
    list_endpoints(
        client,
        [
            "/api/fields/",
            "/api/platforms/",
            "/api/rigs/",
            "/api/wells/",
            "/api/maintenance-windows/",
            "/api/scenarios/",
            "/api/projects/",
            "/api/campaigns/",
            "/api/campaign-projects/",
            "/api/calc-runs/",
        ],
    )

    # CRUD on Field
    crud_field(client)

    print("M2.4/M2.5 smoke test passed.")
