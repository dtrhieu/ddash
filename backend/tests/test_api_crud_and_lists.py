from __future__ import annotations

from pathlib import Path

from django.core import management
import pytest
from rest_framework.test import APIClient

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = [
    str(ROOT / "backend/core/fixtures/initial_core.json"),
    str(ROOT / "backend/scheduling/fixtures/initial_scheduling.json"),
]


@pytest.mark.django_db(transaction=True)
def test_list_endpoints_and_crud_field():
    # Ensure fixtures exist
    for f in FIXTURES:
        assert Path(f).exists(), f"Missing fixture: {f}"

    # Reset DB and load fixtures for deterministic run
    management.call_command("flush", verbosity=0, interactive=False)
    management.call_command("loaddata", *FIXTURES, verbosity=0)

    client = APIClient()

    # List endpoints should return 200 and either list or paginated results
    for ep in [
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
    ]:
        resp = client.get(ep)
        assert resp.status_code == 200, f"GET {ep} -> {resp.status_code}, body={resp.content!r}"
        data = resp.json()
        assert "results" in data or isinstance(data, list), f"Unexpected payload for {ep}: {data}"

    # CRUD for Field entity
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
