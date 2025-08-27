# Drilling Campaign Tracker — Development Plan and TODO

Source spec: [doc/SPEC-002-Drilling Campaign Tracker.md](doc/SPEC-002-Drilling Campaign Tracker.md)

Working mode: Local-first development. All IT/infra hardening is deferred to a later on‑prem phase. This file tracks scope, milestones, and acceptance.

## Scope for MVP (local)

Must-haves:
- Spreadsheet-like UI to CRUD rigs, wells, campaigns
- Gantt chart for campaign schedules with drag/resize and dependencies
- Python calc engine (NPT, utilization, cost/day, ETA) triggerable from UI
- Basic auth with roles (Viewer, Editor, Admin)
- Import/export CSV/Excel
- Audit trail of edits

Should-haves considered for MVP:
- Scenario versions and clone
- Simple API to trigger/fetch calc results

Deferred to IT/on‑prem phase:
- TLS, SMTP, runbooks, backups to enterprise storage, SSO, systemd/production Compose, monitoring/metrics dashboards

## Repo layout (planned)

- backend/ — Django + DRF + Celery + calc
- frontend/ — React + Vite + TypeScript + AG Grid + vis-timeline
- deploy/ — Dockerfiles, docker-compose, nginx
- docs/ — additional docs and ADRs

Key planned files:
- [deploy/docker-compose.yml](deploy/docker-compose.yml)
- [deploy/nginx.conf](deploy/nginx.conf)
- [backend/pyproject.toml](backend/pyproject.toml)
- [backend/manage.py](backend/manage.py)
- [backend/app/settings.py](backend/app/settings.py)
- [backend/app/urls.py](backend/app/urls.py)
- [backend/calc/engine.py](backend/calc/engine.py)
- [frontend/index.html](frontend/index.html)
- [frontend/src/main.tsx](frontend/src/main.tsx)
- [frontend/src/pages/Gantt.tsx](frontend/src/pages/Gantt.tsx)
- [frontend/src/pages/Sheet.tsx](frontend/src/pages/Sheet.tsx)

## Milestones and checklists

### M0 — Project bootstrap

- [x] Initialize git repo, license, editorconfig, README
- [x] Add pre-commit with ruff/black/isort for Python; eslint/prettier for TS
- [x] Decide dependency tooling: pip-tools for backend; pnpm or npm for frontend
- [x] Create base repo structure as above

### M1 — Backend bootstrap

- [ ] Create Django 5.2 project [backend/manage.py](backend/manage.py)
- [ ] Add DRF, CORS, Timezone=UTC, JSON renderer defaults
- [ ] Configure Postgres and Redis settings via env
- [ ] Create base app modules: users, core, scheduling, calc
- [ ] Create initial superuser for local testing

Data model (per spec):
- [ ] User with role enum
- [ ] Rig(name unique, day_rate, status)
- [ ] Well(name unique, field, type)
- [ ] Scenario(name, status, created_by, created_at)
- [ ] Campaign(name, start_date, end_date, scenario_id)
- [ ] CampaignWell(campaign_id, well_id, rig_id, planned/actual dates, dependencies jsonb)
- [ ] CalcRun(scenario_id, status, params jsonb, results jsonb, created_by, timestamps)
- [ ] AuditLog(user_id, entity, entity_id, action, before jsonb, after jsonb, at)
- [ ] Create migrations and apply
- [ ] Add DB indexes: (campaign_id, planned_start), GIN(dependencies), btree(name)

### M2 — AuthZ and Audit

- [ ] Implement session-based auth for local (Django session cookie + CSRF)
- [ ] Roles and DRF permissions for Viewer/Editor/Admin
- [ ] Implement AuditLog via model signals capturing before/after snapshots
- [ ] Add basic admin endpoints for user/role management

### M3 — Core APIs

- [ ] Rigs endpoints GET/POST and GET/PATCH/DELETE by id
- [ ] Wells endpoints GET/POST and GET/PATCH/DELETE by id
- [ ] Scenarios list/create/retrieve/update and POST /clone
- [ ] Campaigns CRUD scoped to scenario
- [ ] CampaignWells CRUD + bulk update
- [ ] Gantt GET /api/gantt/{scenario_id} flattened items grouped by rig
- [ ] Validation and error formatting; filtering/sorting and pagination
- [ ] API tests incl. permission matrix

### M4 — Calc engine

- [ ] Implement pure functions in [backend/calc/engine.py](backend/calc/engine.py)
- [ ] Unit tests for duration, utilization, NPT, cost, ETA
- [ ] Integrate Celery with Redis; local worker process
- [ ] POST /api/calc/run to enqueue; GET /api/calc/{id} to fetch status/results
- [ ] Persist results in CalcRun and return KPIs

Planned functions:
- [ ] [calc.compute_duration()](backend/calc/engine.py:1)
- [ ] [calc.compute_rig_utilization()](backend/calc/engine.py:1)
- [ ] [calc.compute_npt_pct()](backend/calc/engine.py:1)
- [ ] [calc.compute_costs()](backend/calc/engine.py:1)
- [ ] [calc.estimate_eta()](backend/calc/engine.py:1)
- [ ] [calc.run_all_metrics()](backend/calc/engine.py:1)

### M5 — Import/Export

- [ ] CSV/Excel import with pandas/openpyxl
- [ ] Column mapping UI and dry-run response
- [ ] Export endpoints for rigs/wells/campaign-wells
- [ ] Dataset validators and error reporting

### M6 — Frontend scaffold

- [ ] Vite + React + TypeScript app [frontend/src/main.tsx](frontend/src/main.tsx)
- [ ] API client with fetch wrapper, auth handling, error mapping
- [ ] Routing and protected routes by role
- [ ] Authentication UI (login/logout), session storage, CSRF handling

### M7 — UI Features

Sheet View:
- [ ] AG Grid with columns: rig, well, planned_start/end, duration, cost
- [ ] CRUD with inline validation; undo/redo; multi-row paste
- [ ] Optimistic updates with server reconciliation

Gantt View:
- [ ] vis-timeline grouped by rig
- [ ] Drag/resize dates; display dependencies
- [ ] Context menu add/remove

Scenario UX:
- [ ] Scenario switcher dropdown; clone action; status badges

Calc Panel:
- [ ] Trigger calc run; poll status; render KPIs; download JSON/CSV

Import/Export UI:
- [ ] Column mapping and dry-run preview; progress and error states

### M8 — Tests and quality

- [ ] Backend: pytest config, API tests, calc unit tests
- [ ] Frontend: vitest/react-testing-library unit tests
- [ ] E2E: Playwright happy-path for Sheet, Gantt, Calc
- [ ] Lint/format CI and pre-commit hooks

### M9 — Local packaging and data

- [ ] Dockerfiles for backend and frontend
- [ ] Nginx reverse proxy config [deploy/nginx.conf](deploy/nginx.conf)
- [ ] docker-compose for nginx, django, celery, redis, postgres [deploy/docker-compose.yml](deploy/docker-compose.yml)
- [ ] .env.example for services and Makefile targets
- [ ] Seed sample data fixtures and a demo scenario

### M10 — Deferred IT/on‑prem hardening (placeholder)

- [ ] TLS termination with enterprise certs
- [ ] Backups: nightly pg_dump, weekly base + WAL to enterprise storage
- [ ] Monitoring/log shipping, request IDs, dashboards
- [ ] SMTP notifications for schedule changes
- [ ] SSO integration
- [ ] Systemd or production Compose, rollout runbooks

## Acceptance checklist (maps to spec)

- [ ] CRUD via grid with inline edit, sorting/filtering
- [ ] Gantt with drag/resize and dependency display
- [ ] Trigger calcs and see results; KPIs visible
- [ ] Roles enforced across endpoints and UI routes
- [ ] CSV/Excel import/export round-trips
- [ ] Audit trail captures who/when/what before/after

## Interfaces summary

Backend endpoints:
- [ ] /api/rigs/ and /api/rigs/{id}
- [ ] /api/wells/ and /api/wells/{id}
- [ ] /api/scenarios/ and /api/scenarios/clone
- [ ] /api/campaigns/ and /api/campaigns/{id}
- [ ] /api/campaign-wells/ (+ bulk)
- [ ] /api/gantt/{scenario_id}
- [ ] /api/calc/run and /api/calc/{calc_run_id}
- [ ] /api/import and /api/export

Frontend routes (planned):
- [ ] /login
- [ ] /sheet
- [ ] /gantt
- [ ] /calc
- [ ] /import-export

## Notes

- Local dev authentication: session cookie and CSRF for simplicity; can swap to JWT later if needed.
- Visibility: keep this TODO evolving; add dates/owners when tasks start.
- Link back to spec for details: [doc/SPEC-002-Drilling Campaign Tracker.md](doc/SPEC-002-Drilling Campaign Tracker.md)

## Quick next actions

- [x] Create repo structure
- [ ] Bootstrap Django + DRF + Postgres + Redis
- [ ] Scaffold React + Vite + TS
- [ ] Define API contracts for M3 and stub endpoints
- [ ] Add sample data and smoke test list endpoints