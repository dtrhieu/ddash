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

### M1.1 — Backend project bootstrap (framework and runtime)

- [x] M1.1.1 Create Django 5.2 project "app" with manage.py, settings, urls, asgi, wsgi in backend [backend/manage.py](backend/manage.py)
- [x] M1.1.2 Add DRF to INSTALLED_APPS and set default JSON renderer in settings [backend/app/settings.py](backend/app/settings.py)
- [x] M1.1.3 Add and configure django-cors-headers; set TIME_ZONE=UTC and USE_TZ=True [backend/app/settings.py](backend/app/settings.py)
- [x] M1.1.4 Configure Postgres and Redis via env vars in settings; add backend/.env.example with local defaults [backend/app/settings.py](backend/app/settings.py)
- [x] M1.1.5 Introduce pip-tools: add backend/requirements.in and requirements-dev.in; compile to requirements.txt and requirements-dev.txt
- [x] M1.1.6 Implement /api/health endpoint and wire it in urls for smoke testing [backend/app/urls.py](backend/app/urls.py)
- [x] M1.1.7 Run initial migrations and verify runserver boots locally

### M1.2 — Base apps and data model (domain entities)

- [ ] M1.2.1 Create Django apps: users, core, scheduling, calc
- [ ] M1.2.2 Implement models per spec: User(role enum), Rig, Well, Scenario, Campaign, CampaignWell, CalcRun, AuditLog
- [ ] M1.2.3 Add DB indexes and constraints: btree(name), composite (campaign_id, planned_start), GIN on dependencies jsonb
- [ ] M1.2.4 Make and apply initial migrations
- [ ] M1.2.5 Register models in Django admin for visibility
- [ ] M1.2.6 Create initial superuser for local testing
- [ ] M1.2.7 Seed minimal sample fixtures for rigs/wells/campaign-wells
- [ ] M1.2.8 Smoke test via Django shell to create/list entities and validate constraints

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

#### M6.1 — Project Setup
- [x] M6.1.1 Set up Vite + React + TypeScript project with package.json and dependencies
- [x] M6.1.2 Configure Vite build system and development server
- [x] M6.1.3 Set up project structure with components, hooks, utils, and types directories

#### M6.2 — API Client & Auth
- [ ] M6.2.1 Create API client with fetch wrapper and base configuration
- [ ] M6.2.2 Implement authentication handling (login/logout/session management)
- [ ] M6.2.3 Add error mapping and response handling utilities
- [ ] M6.2.4 Create TypeScript types for API responses and requests

#### M6.3 — Routing & Protection
- [ ] M6.3.1 Set up React Router for navigation
- [ ] M6.3.2 Implement protected routes with role-based access control
- [ ] M6.3.3 Create route guards and authentication checks

#### M6.4 — Authentication UI
- [ ] M6.4.1 Create login page component with form validation
- [ ] M6.4.2 Implement logout functionality and session cleanup
- [ ] M6.4.3 Add loading states and error handling for auth flows

#### M6.5 — Session & Security
- [ ] M6.5.1 Implement session storage for authentication tokens
- [ ] M6.5.2 Add CSRF token handling for API requests
- [ ] M6.5.3 Create authentication context/provider for global state management

#### M6.6 — Integration & Layout
- [ ] M6.6.1 Update main.tsx to use router and authentication provider
- [ ] M6.6.2 Connect existing Gantt and Sheet pages to the routing system
- [ ] M6.6.3 Add navigation layout with role-based menu items

#### M6.7 — Testing & Verification
- [ ] M6.7.1 Test complete authentication flow (login → protected routes → logout)
- [ ] M6.7.2 Verify API client integration with backend endpoints
- [ ] M6.7.3 Ensure proper error handling and user feedback throughout the app

### M7 — UI Features

#### M7.1 — Sheet View Implementation
- [x] M7.1.1 Set up AG Grid component with basic configuration and data source
- [x] M7.1.2 Configure columns: rig, well, planned_start/end, duration, cost with proper formatting
  - Implemented: AG Grid Community with sorting, filtering, pagination, date/currency formatting, calculated duration and cost columns
- [ ] M7.1.3 Implement Create operations (add new rows/campaign-wells)
- [ ] M7.1.4 Implement Read operations (display data with sorting/filtering)
- [ ] M7.1.5 Implement Update operations (inline editing)
- [ ] M7.1.6 Implement Delete operations (remove rows with confirmation)
- [ ] M7.1.7 Add inline validation for data entry (required fields, date formats, numeric ranges)
- [ ] M7.1.8 Implement undo/redo functionality with state management
- [ ] M7.1.9 Add multi-row paste support with data parsing
- [ ] M7.1.10 Implement optimistic updates for better UX
- [ ] M7.1.11 Add server reconciliation for conflict resolution and error handling

#### M7.2 — Gantt View Implementation
- [ ] M7.2.1 Set up vis-timeline component with basic configuration
- [ ] M7.2.2 Group timeline items by rig with proper visualization
- [ ] M7.2.3 Implement drag functionality for changing dates
- [ ] M7.2.4 Implement resize functionality for duration changes
- [ ] M7.2.5 Display dependencies between campaign items with visual connectors
- [ ] M7.2.6 Add context menu for add/remove operations
- [ ] M7.2.7 Implement real-time updates when data changes in other views

#### M7.3 — Scenario UX Implementation
- [ ] M7.3.1 Create scenario switcher dropdown component
- [ ] M7.3.2 Implement scenario selection and context switching
- [ ] M7.3.3 Add clone action functionality with naming dialog
- [ ] M7.3.4 Display status badges (active, draft, archived) for scenarios
- [ ] M7.3.5 Add scenario creation and management controls

#### M7.4 — Calc Panel Implementation
- [ ] M7.4.1 Create calc trigger button/component with loading states
- [ ] M7.4.2 Implement polling mechanism for calc run status updates
- [ ] M7.4.3 Render KPIs in organized panel layout (utilization, NPT, costs, ETA)
- [ ] M7.4.4 Add download functionality for JSON results
- [ ] M7.4.5 Add download functionality for CSV export of calc results
- [ ] M7.4.6 Handle calc errors and display user-friendly messages

#### M7.5 — Import/Export UI Implementation
- [ ] M7.5.1 Create column mapping interface for CSV/Excel imports
- [ ] M7.5.2 Implement dry-run preview functionality with data validation
- [ ] M7.5.3 Add progress indicators for import/export operations
- [ ] M7.5.4 Handle and display validation errors with specific field highlighting
- [ ] M7.5.5 Implement error recovery and retry mechanisms
- [ ] M7.5.6 Add export functionality with format selection (CSV/Excel)

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
- Link back to spec for details: [docs/SPEC-002-Drilling Campaign Tracker.md](docs/SPEC-002-Drilling%20Campaign%20Tracker.md)

## Quick next actions

- [x] Create repo structure
- [ ] Bootstrap Django + DRF + Postgres + Redis
- [x] Scaffold React + Vite + TS (M6.1 + M7.1.1-2 completed)
- [ ] Define API contracts for M3 and stub endpoints
- [ ] Add sample data and smoke test list endpoints
