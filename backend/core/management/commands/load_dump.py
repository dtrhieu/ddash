from __future__ import annotations

import csv
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.dateparse import parse_date

from core.models import Field, MaintenanceWindow, Platform, Rig, Well
from scheduling.models import CalcRun, Campaign, CampaignProject, Project, Scenario


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        return [dict(row) for row in csv.DictReader(f)]


def read_json(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        for k in ("items", "data", "results"):
            v = data.get(k)
            if isinstance(v, list):
                data = v
                break
    if not isinstance(data, list):
        raise CommandError(f"JSON must be an array: {path}")
    return [dict(x) for x in data]


def parse_bool(val: str | None) -> bool | None:
    if val is None or val == "":
        return None
    return str(val).strip().lower() in {"1", "true", "yes", "y"}


def parse_decimal(val: str | None) -> Any:
    from decimal import Decimal

    if val is None or val == "":
        return None
    return Decimal(str(val))


def parse_uuid(val: str | None):
    import uuid

    if not val:
        return None
    return uuid.UUID(str(val))


def parse_date_opt(val: str | None):
    if not val:
        return None
    return parse_date(val)


@dataclass
class LoadContext:
    dump_dir: Path
    dry_run: bool
    default_user: Any


class Command(BaseCommand):
    help = "Load CSV dump into Django models (real app DB)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dump",
            help="Path to dump directory (default: scripts/dump_data/drilling_campaign_2025)",
        )
        parser.add_argument("--dry-run", action="store_true", help="Validate without writing")
        parser.add_argument(
            "--create-superuser",
            action="store_true",
            help="Create a default superuser admin/admin if missing (local only)",
        )

    def handle(self, *args, **options):
        dump_dir = (
            Path(options["dump"]).resolve()
            if options.get("dump")
            else Path(__file__).resolve().parents[4]
            / "scripts"
            / "dump_data"
            / "drilling_campaign_2025"
        )
        if not dump_dir.exists():
            raise CommandError(f"Dump directory not found: {dump_dir}")

        User = get_user_model()
        if options.get("create_superuser") and not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin")
            self.stdout.write(self.style.SUCCESS("Created superuser admin/admin"))

        # Ensure at least one user exists for created_by fields
        default_user = User.objects.first()
        if not default_user:
            default_user = User.objects.create_user(username="loader", password="loader")

        ctx = LoadContext(dump_dir=dump_dir, dry_run=options["dry_run"], default_user=default_user)

        loaders: list[tuple[str, callable]] = [
            ("fields.csv", lambda p: self.load_fields(ctx, p)),
            ("platforms.csv", lambda p: self.load_platforms(ctx, p)),
            ("rigs.csv", lambda p: self.load_rigs(ctx, p)),
            ("wells.csv", lambda p: self.load_wells(ctx, p)),
            ("maintenance_windows.csv", lambda p: self.load_maintenance(ctx, p)),
            ("scenarios.csv", lambda p: self.load_scenarios(ctx, p)),
            ("projects.csv", lambda p: self.load_projects(ctx, p)),
            ("campaigns.csv", lambda p: self.load_campaigns(ctx, p)),
            ("campaign_projects.csv", lambda p: self.load_campaign_projects(ctx, p)),
            ("calc_runs.csv", lambda p: self.load_calc_runs(ctx, p)),
        ]

        with transaction.atomic():
            total = 0
            for filename, fn in loaders:
                path = ctx.dump_dir / filename
                if not path.exists():
                    continue
                n = fn(path)
                self.stdout.write(f"Loaded {n} from {filename}")
                total += n
            self.stdout.write(self.style.SUCCESS(f"Done. Inserted {total} rows."))
            if ctx.dry_run:
                self.stdout.write(self.style.WARNING("Dry-run: rolling back transaction"))
                raise transaction.TransactionManagementError("dry-run rollback")

    # Loader implementations
    def load_fields(self, ctx: LoadContext, path: Path) -> int:
        rows = read_csv(path) if path.suffix == ".csv" else read_json(path)
        objs: list[Field] = []
        for r in rows:
            objs.append(
                Field(
                    id=parse_uuid(r.get("id")) or None,
                    name=r.get("name") or "",
                )
            )
        Field.objects.bulk_create(objs, ignore_conflicts=True)
        return len(objs)

    def load_platforms(self, ctx: LoadContext, path: Path) -> int:
        rows = read_csv(path) if path.suffix == ".csv" else read_json(path)
        created = 0
        for r in rows:
            field = None
            field_id = r.get("field_id")
            if field_id:
                field = Field.objects.filter(id=parse_uuid(field_id)).first()
            if not field and r.get("field_name"):
                field = Field.objects.filter(name=r["field_name"]).first()
            if not field:
                continue
            obj_id = parse_uuid(r.get("id"))
            name = r.get("name") or ""
            status = r.get("status") or Platform.Status.OPERATING
            if obj_id:
                Platform.objects.update_or_create(
                    id=obj_id, defaults={"field": field, "name": name, "status": status}
                )
            else:
                Platform.objects.get_or_create(field=field, name=name, defaults={"status": status})
            created += 1
        return created

    def load_rigs(self, ctx: LoadContext, path: Path) -> int:
        rows = read_csv(path) if path.suffix == ".csv" else read_json(path)
        objs: list[Rig] = []
        for r in rows:
            objs.append(
                Rig(
                    id=parse_uuid(r.get("id")) or None,
                    name=r.get("name") or "",
                    rig_kind=r.get("rig_kind") or Rig.RigKind.JACKUP,
                    day_rate=parse_decimal(r.get("day_rate")) or 0,
                    status=r.get("status") or Rig.Status.ACTIVE,
                )
            )
        Rig.objects.bulk_create(objs, ignore_conflicts=True)
        return len(objs)

    def load_wells(self, ctx: LoadContext, path: Path) -> int:
        rows = read_csv(path) if path.suffix == ".csv" else read_json(path)
        created = 0
        for r in rows:
            field = Field.objects.filter(id=parse_uuid(r.get("field_id"))).first()
            if not field and r.get("field_name"):
                field = Field.objects.filter(name=r["field_name"]).first()
            if not field:
                continue
            platform = None
            pid = r.get("platform_id")
            if pid:
                platform = Platform.objects.filter(id=parse_uuid(pid)).first()
            elif r.get("platform_name"):
                platform = Platform.objects.filter(field=field, name=r["platform_name"]).first()
            _wid = parse_uuid(r.get("id"))
            if _wid:
                Well.objects.update_or_create(
                    id=_wid,
                    defaults={
                        "name": r.get("name") or "",
                        "field": field,
                        "platform": platform,
                        "well_kind": r.get("well_kind") or Well.WellKind.PLATFORM_WELL,
                        "type": r.get("type") or Well.Type.DEVELOPMENT,
                        "lat": parse_decimal(r.get("lat")),
                        "lon": parse_decimal(r.get("lon")),
                    },
                )
            created += 1
        return created

    def load_maintenance(self, ctx: LoadContext, path: Path) -> int:
        rows = read_csv(path) if path.suffix == ".csv" else read_json(path)
        created = 0
        for r in rows:
            platform = None
            pid = r.get("platform_id")
            if pid:
                platform = Platform.objects.filter(id=parse_uuid(pid)).first()
            elif r.get("platform_name"):
                platform = Platform.objects.filter(name=r["platform_name"]).first()
            if not platform:
                continue
            MaintenanceWindow.objects.update_or_create(
                id=parse_uuid(r.get("id")) or None,
                defaults={
                    "platform": platform,
                    "start_date": parse_date(r.get("start_date")),
                    "end_date": parse_date(r.get("end_date")),
                    "reason": r.get("reason") or "",
                },
            )
            created += 1
        return created

    def load_scenarios(self, ctx: LoadContext, path: Path) -> int:
        rows = read_csv(path) if path.suffix == ".csv" else read_json(path)
        objs: list[Scenario] = []
        for r in rows:
            objs.append(
                Scenario(
                    id=parse_uuid(r.get("id")) or None,
                    name=r.get("name") or "",
                    status=r.get("status") or Scenario.Status.DRAFT,
                    created_by=ctx.default_user,
                )
            )
        Scenario.objects.bulk_create(objs, ignore_conflicts=True)
        return len(objs)

    def load_projects(self, ctx: LoadContext, path: Path) -> int:
        rows = read_csv(path) if path.suffix == ".csv" else read_json(path)
        created = 0
        for r in rows:
            field = Field.objects.filter(id=parse_uuid(r.get("field_id"))).first()
            platform = Platform.objects.filter(id=parse_uuid(r.get("platform_id"))).first()
            well = Well.objects.filter(id=parse_uuid(r.get("well_id"))).first()
            rig = Rig.objects.filter(id=parse_uuid(r.get("rig_id"))).first()
            Project.objects.update_or_create(
                id=parse_uuid(r.get("id")) or None,
                defaults={
                    "name": r.get("name") or "",
                    "project_type": r.get("project_type") or Project.ProjectType.OTHER,
                    "field": field,
                    "platform": platform,
                    "well": well,
                    "rig": rig,
                    "status": r.get("status") or Project.Status.PLANNED,
                    "planned_start": parse_date(r.get("planned_start")),
                    "planned_end": parse_date(r.get("planned_end")),
                    "actual_start": parse_date_opt(r.get("actual_start")),
                    "actual_end": parse_date_opt(r.get("actual_end")),
                    "dependencies": self._parse_json_safe(r.get("dependencies")) or {},
                    "extras": self._parse_json_safe(r.get("extras")) or {},
                },
            )
            created += 1
        return created

    def load_campaigns(self, ctx: LoadContext, path: Path) -> int:
        rows = read_csv(path) if path.suffix == ".csv" else read_json(path)
        created = 0
        for r in rows:
            scenario = Scenario.objects.filter(id=parse_uuid(r.get("scenario_id"))).first()
            if not scenario:
                scenario = Scenario.objects.first()
            # If no scenarios exist at all, create a default one
            if not scenario:
                scenario = Scenario.objects.create(
                    name="Default Scenario",
                    status=Scenario.Status.DRAFT,
                    created_by=ctx.default_user,
                )
            rig = Rig.objects.filter(id=parse_uuid(r.get("rig_id"))).first()
            field = Field.objects.filter(id=parse_uuid(r.get("field_id"))).first()
            Campaign.objects.update_or_create(
                id=parse_uuid(r.get("id")) or None,
                defaults={
                    "name": r.get("name") or "",
                    "campaign_type": r.get("campaign_type") or Campaign.CampaignType.RIG_CAMPAIGN,
                    "scenario": scenario,
                    "rig": rig,
                    "field": field,
                },
            )
            created += 1
        return created

    def load_campaign_projects(self, ctx: LoadContext, path: Path) -> int:
        rows = read_csv(path) if path.suffix == ".csv" else read_json(path)
        created = 0
        for r in rows:
            campaign = Campaign.objects.filter(id=parse_uuid(r.get("campaign_id"))).first()
            project = Project.objects.filter(id=parse_uuid(r.get("project_id"))).first()
            if not campaign or not project:
                continue
            CampaignProject.objects.get_or_create(campaign=campaign, project=project)
            created += 1
        return created

    def load_calc_runs(self, ctx: LoadContext, path: Path) -> int:
        rows = read_csv(path) if path.suffix == ".csv" else read_json(path)
        objs: list[CalcRun] = []
        scenario = Scenario.objects.first()
        for r in rows:
            objs.append(
                CalcRun(
                    id=parse_uuid(r.get("id")) or None,
                    scenario=scenario,
                    status=r.get("status") or CalcRun.Status.PENDING,
                    params=self._parse_json_safe(r.get("params")) or {},
                    results=self._parse_json_safe(r.get("results")) or {},
                    created_by=ctx.default_user,
                )
            )
        CalcRun.objects.bulk_create(objs, ignore_conflicts=True)
        return len(objs)

    def _parse_json_safe(self, s: str | None) -> dict[str, Any] | list[Any] | None:
        if not s:
            return None
        try:
            return json.loads(s)
        except Exception:
            return None
