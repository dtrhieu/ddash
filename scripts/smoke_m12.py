#!/usr/bin/env python3
"""
Smoke test for M1.2 seed and constraints.
- Sets up Django
- Loads fixtures (core + scheduling)
- Runs a few basic validations/queries

Usage:
  python3 scripts/smoke_m12.py
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

from django.core import management  # noqa: E402
from core.models import MaintenanceWindow, Platform  # noqa: E402
from scheduling.models import Campaign, CampaignProject, Project, Scenario  # noqa: E402


def load_fixtures():
    fixtures = [
        str(ROOT / "backend/core/fixtures/initial_core.json"),
        str(ROOT / "backend/scheduling/fixtures/initial_scheduling.json"),
    ]
    for f in fixtures:
        if not Path(f).exists():
            raise SystemExit(f"Missing fixture: {f}")
    # Ensure deterministic runs: wipe existing data before loading fixtures
    management.call_command("flush", verbosity=0, interactive=False)
    management.call_command("loaddata", *fixtures, verbosity=1)


def check_constraints():
    # Ensure records present
    assert Scenario.objects.count() >= 1
    assert Campaign.objects.count() >= 1
    assert Project.objects.count() >= 2

    # Maintenance overlap detection for Platform A
    platform = Platform.objects.get(name="Platform A")
    mw = MaintenanceWindow.objects.filter(platform=platform).first()
    assert mw is not None

    overlapping = Project.objects.filter(
        platform=platform,
        planned_start__lte=mw.end_date,
        planned_end__gte=mw.start_date,
    )
    print(
        f"Overlapping projects with maintenance window: {[p.name for p in overlapping]}"
    )
    assert (
        overlapping.exists()
    ), "Expected at least one overlapping project with maintenance window"

    # Campaign-project linkage exists
    cps = CampaignProject.objects.filter(campaign__name="Rig Alpha 2025")
    assert cps.count() == 2


def check_health_endpoint():
    from django.test import Client

    client = Client()
    resp = client.get("/api/health")
    assert resp.status_code == 200, f"/api/health returned {resp.status_code}"
    data = resp.json()
    assert data.get("ok") is True
    assert data.get("service") == "ddash-backend"


if __name__ == "__main__":
    load_fixtures()
    check_constraints()
    print("M1.2 smoke test passed.")
