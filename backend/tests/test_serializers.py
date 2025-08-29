from __future__ import annotations

import datetime as dt
import os
from pathlib import Path
import sys

import django
from django.test import TestCase

from core.models import Field as CoreField, Platform, Rig, Well
from core.serializers import (
    FieldSerializer,
    WellSerializer,
)
from scheduling.models import Project
from scheduling.serializers import ProjectSerializer

# Configure Django for tests run via `python -m unittest`
ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
sys.path.insert(0, str(ROOT / "backend"))

django.setup()


class SerializerSmokeTests(TestCase):
    def setUp(self) -> None:
        self.field = CoreField.objects.create(name="Alpha")
        self.platform = Platform.objects.create(field=self.field, name="P1")
        self.rig = Rig.objects.create(name="R1", rig_kind=Rig.RigKind.JACKUP, day_rate=1000)

    def test_field_serializer_roundtrip(self):
        ser = FieldSerializer(data={"name": "Beta"})
        self.assertTrue(ser.is_valid(), ser.errors)
        inst = ser.save()
        ser2 = FieldSerializer(instance=inst)
        self.assertEqual(ser2.data["name"], "Beta")

    def test_well_platform_validation(self):
        # Platform well must have platform
        ser = WellSerializer(
            data={
                "name": "W1",
                "field": str(self.field.id),
                "well_kind": Well.WellKind.PLATFORM_WELL,
                "type": Well.Type.DEVELOPMENT,
            }
        )
        self.assertFalse(ser.is_valid())
        self.assertIn("platform", ser.errors)

        ser2 = WellSerializer(
            data={
                "name": "W2",
                "field": str(self.field.id),
                "platform": str(self.platform.id),
                "well_kind": Well.WellKind.PLATFORM_WELL,
                "type": Well.Type.DEVELOPMENT,
            }
        )
        self.assertTrue(ser2.is_valid(), ser2.errors)
        self.assertIsNotNone(ser2.save())

    def test_project_dates_validation(self):
        data = {
            "name": "Proj1",
            "project_type": Project.ProjectType.DRILLING,
            "planned_start": dt.date(2025, 1, 10),
            "planned_end": dt.date(2025, 1, 5),
        }
        ser = ProjectSerializer(data=data)
        self.assertFalse(ser.is_valid())
        self.assertIn("planned_end", ser.errors)

        data["planned_end"] = dt.date(2025, 1, 15)
        ser2 = ProjectSerializer(data=data)
        self.assertTrue(ser2.is_valid(), ser2.errors)
