# Drilling Campaign Tracker — Development Plan and TODO

Source spec: [docs/SPEC-002-Drilling Campaign Tracker.md](docs/SPEC-002-Drilling%20Campaign%20Tracker.md)

Working mode: Local-first development. All IT/infra hardening is deferred to a later on‑prem phase. This file tracks scope, milestones, and acceptance.

## Scope for MVP (local) - REVISED

**Phase 1 Must-haves (Sheet-First Approach):**
- Spreadsheet-like UI to CRUD Fields, Platforms, Wells, Projects, Campaigns (with relations and inline editing)
- REST API endpoints for all core entities with full CRUD operations
- Basic Python calc engine: duration, cost calculation, simple conflict detection (rig double-booking)
- Gantt chart of Projects with basic drag/resize functionality
- Simple data import/export (CSV) for core entities

**Phase 2 Should-haves (Enhanced Features):**
- Advanced Gantt features: grouping by Rig/Platform/Field, dependencies, maintenance window overlays
- Enhanced calc engine: rig utilization, ETA, platform maintenance clash detection
- Scenario versions and clone functionality
- Excel import/export with column mapping

**Deferred to Later Phases:**
- User auth with roles (Viewer, Editor, Admin) - **DEFERRED**
- Audit trail of edits - **DEFERRED**
- Comments/annotations on grid rows and Gantt items
- Map view for open-location exploration wells
- TLS, SMTP, runbooks, backups to enterprise storage, SSO, production Compose/systemd, monitoring/metrics dashboards

## Repo layout (planned)

- backend/ — Django + DRF + Celery + calc
- frontend/ — React + Vite + TypeScript + AG Grid + frappe-gantt
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

- [x] M1.2.1 Create Django apps: users, core, scheduling, calc
  - Note: users/core/scheduling scaffolds added and wired into INSTALLED_APPS; calc remains a pure module under backend/calc. To avoid name collision, decide an app name like "calc_models" later.
- [x] M1.2.2 Implement models per spec: User(role enum), Field, Platform, Rig, Well, Project, Campaign, CampaignProject (junction), Scenario, CalcRun, MaintenanceWindow, AuditLog
- [ ] M1.2.3 Add DB indexes and constraints: unique(name) where applicable; btree(name); composites on Project (rig_id, planned_start), (platform_id, planned_start); GIN on dependencies jsonb
  - Status: unique(name) and btree indexes added where applicable; composites present on Project; GIN on dependencies will be added only for Postgres via a follow-up migration (SQLite skip). Planned migration name: scheduling 0002_add_gin_index_dependencies (conditional on PostgreSQL).
- [x] M1.2.4 Make and apply initial migrations
  - Users/core/scheduling 0001_initial created on 2025-08-29; apply with: python backend/manage.py migrate
- [x] M1.2.5 Register models in Django admin for visibility
  - Admins added for users.User, core.Field/Platform/Rig/Well/MaintenanceWindow/AuditLog, scheduling.Scenario/Project/Campaign/CampaignProject/CalcRun; with basic list_display, filters, search.
- [x] M1.2.6 Create initial superuser for local testing
  - Plan: run python backend/manage.py createsuperuser; or set DJANGO_SUPERUSER_USERNAME, EMAIL, PASSWORD and run python backend/manage.py createsuperuser --noinput (documented below).
- [x] M1.2.7 Seed minimal sample fixtures for fields/platforms/wells/rigs/projects/campaigns/maintenance-windows
  - Implemented: JSON fixtures added under backend/core/fixtures/initial_core.json and backend/scheduling/fixtures/initial_scheduling.json. Load via: python backend/manage.py loaddata backend/core/fixtures/initial_core.json backend/scheduling/fixtures/initial_scheduling.json.
- [x] M1.2.8 Smoke test via Django shell to create/list entities and validate constraints (rig-required types, maintenance clash)
  - Implemented: scripts/smoke_m12.py verifies maintenance overlap and campaign ordering. Run with: python scripts/smoke_m12.py.

### M2 — Core APIs (PRIORITY 1 - MVP Phase 1)

- [x] M2.1 Create DRF serializers for all core entities (Field, Platform, Rig, Well, Project, Campaign)
- [x] M2.2 Implement ViewSets with full CRUD operations for all entities
- [x] M2.3 Add proper validation and error handling in serializers
- [x] M2.4 Wire up URL routing for all API endpoints (/api/fields/, /api/platforms/, etc.)
- [x] M2.5 Load sample data fixtures and test all endpoints
- [x] M2.6 Create API documentation and test basic operations

### M3 — Sheet-Like UI Foundation (PRIORITY 2 - MVP Phase 1)

- [ ] M3.1 Create TypeScript API client with proper error handling
- [ ] M3.2 Build type definitions matching backend models
- [ ] M3.3 Implement CRUD operations for all entities in API client
- [ ] M3.4 Create base AG Grid components with proper configuration
- [ ] M3.5 Build individual entity management sheets (Fields, Platforms, Rigs, Wells)
- [ ] M3.6 Implement comprehensive Projects sheet as main interface
- [ ] M3.7 Add inline editing, validation, and relationship handling
- [ ] M3.8 Implement filtering, sorting, and basic bulk operations

### M4 — Basic Calculation Engine (PRIORITY 3 - MVP Phase 1)

- [ ] Implement real duration and cost calculations in [backend/calc/engine.py](backend/calc/engine.py)
- [ ] Add basic rig double-booking conflict detection
- [ ] Create simple rig utilization metrics
- [ ] Add calculation trigger API endpoint
- [ ] Display calculation results in UI panel
- [ ] Show conflicts and warnings in sheet views

### M5 — Enhanced Gantt View (PRIORITY 4 - MVP Phase 1)

- [ ] Connect Gantt component to real project data from API
- [ ] Transform project data to frappe-gantt format
- [ ] Implement drag and drop to update project dates
- [ ] Add basic grouping toggle (by rig/platform/field)
- [ ] Show conflict highlighting in timeline
- [ ] Handle data updates and refresh from sheet changes

### M6 — Data Import/Export (PRIORITY 5 - MVP Phase 1)

- [ ] Implement CSV export for all entity types
- [ ] Add basic CSV import with column mapping
- [ ] Create import validation and error reporting
- [ ] Add dry-run preview functionality
- [ ] Excel export with proper formatting (Phase 2)

### M7 — DEFERRED: AuthZ and Audit (MVP Phase 2)

- [ ] Implement session-based auth for local (Django session cookie + CSRF)
- [ ] Roles and DRF permissions for Viewer/Editor/Admin
- [ ] Implement AuditLog via model signals capturing before/after snapshots
- [ ] Add basic admin endpoints for user/role management

### M8 — DEFERRED: Advanced Features (MVP Phase 2)

- [ ] Advanced Gantt features: dependencies, maintenance window overlays
- [ ] Scenario versions and clone functionality
- [ ] Comments/annotations system
- [ ] Map view for exploration wells
- [ ] Excel import/export with advanced column mapping

### M9 — REVISED: Frontend Implementation (MVP Phase 1)

#### M9.1 — API Client Foundation (PRIORITY 1)
- [x] M9.1.1 Set up Vite + React + TypeScript project with package.json and dependencies
- [x] M9.1.2 Configure Vite build system and development server
- [x] M9.1.3 Set up project structure with components, hooks, utils, and types directories
- [ ] M9.1.4 Create API client with fetch wrapper and base configuration
- [ ] M9.1.5 Add error mapping and response handling utilities
- [ ] M9.1.6 Create TypeScript types for API responses and requests

#### M9.2 — Sheet View Implementation (PRIORITY 2)
- [x] M9.2.1 Set up AG Grid component with basic configuration and data source
- [x] M9.2.2 Configure columns: rig, well, planned_start/end, duration, cost with proper formatting
- [ ] M9.2.3 Build individual entity management sheets (Fields, Platforms, Rigs, Wells)
- [ ] M9.2.4 Implement comprehensive Projects sheet as main interface
- [ ] M9.2.5 Implement Create operations (add new rows for all entity types)
- [ ] M9.2.6 Implement Update operations (inline editing with validation)
- [ ] M9.2.7 Implement Delete operations (remove rows with confirmation)
- [ ] M9.2.8 Add relationship handling (dropdowns for foreign keys)
- [ ] M9.2.9 Implement filtering, sorting, and basic bulk operations

#### M9.3 — Gantt View Enhancement (PRIORITY 3)
- [x] M9.3.1 Install frappe-gantt and create React wrapper component
- [ ] M9.3.2 Connect Gantt to real project data from API
- [ ] M9.3.3 Wire up drag/resize events to update project dates via API
- [ ] M9.3.4 Add basic grouping toggle (by rig/platform/field)
- [ ] M9.3.5 Show conflict highlighting in timeline
- [ ] M9.3.6 Handle data updates and refresh from sheet changes

#### M9.4 — Calculation Panel (PRIORITY 4)
- [ ] M9.4.1 Create calc trigger button/component with loading states
- [ ] M9.4.2 Display calculation results in organized panel layout
- [ ] M9.4.3 Show conflicts and warnings from calculations
- [ ] M9.4.4 Add basic export functionality for calc results

#### M9.5 — Import/Export UI (PRIORITY 5)
- [ ] M9.5.1 Add CSV export functionality for all entity types
- [ ] M9.5.2 Create basic CSV import with column mapping
- [ ] M9.5.3 Implement import validation and error reporting
- [ ] M9.5.4 Add dry-run preview functionality

#### M9.6 — DEFERRED: Authentication UI (MVP Phase 2)
- [ ] Create login page component with form validation
- [ ] Implement logout functionality and session cleanup
- [ ] Add loading states and error handling for auth flows
- [ ] Implement protected routes with role-based access control
- [ ] Create authentication context/provider for global state management

#### M9.7 — DEFERRED: Advanced Features (MVP Phase 2)
- [ ] Advanced Gantt features: dependencies, maintenance window overlays
- [ ] Scenario management UI with clone functionality
- [ ] Comments/annotations system
- [ ] Map view for exploration wells
- [ ] Advanced import/export with Excel support

### M10 — Tests and quality

- [ ] M10.1 Backend: pytest config, API tests, calc unit tests
- [ ] M10.2 Frontend: vitest/react-testing-library unit tests
- [ ] M10.3 E2E: Playwright happy-path for Sheet, Gantt, Calc
- [ ] M10.4 Lint/format CI and pre-commit hooks

### M11 — Local packaging and data

- [ ] Dockerfiles for backend and frontend
- [ ] Nginx reverse proxy config [deploy/nginx.conf](deploy/nginx.conf)
- [ ] docker-compose for nginx, django, celery, redis, postgres [deploy/docker-compose.yml](deploy/docker-compose.yml)
- [ ] .env.example for services and Makefile targets
- [ ] Seed sample data fixtures and a demo scenario

### M12 — Deferred IT/on‑prem hardening (placeholder)

- [ ] TLS termination with enterprise certs
- [ ] Backups: nightly pg_dump, weekly base + WAL to enterprise storage
- [ ] Monitoring/log shipping, request IDs, dashboards
- [ ] SMTP notifications for schedule changes
- [ ] SSO integration
- [ ] Systemd or production Compose, rollout runbooks

## Acceptance checklist (MVP Phase 1)

**Core Functionality:**
- [ ] CRUD via grid with inline edit, sorting/filtering across Fields, Platforms, Wells, Projects, Campaigns
- [ ] REST API endpoints working for all core entities with proper validation
- [ ] Basic calculations working: duration, cost, simple conflict detection
- [ ] Gantt with drag/resize and basic grouping toggle Rig/Platform/Field
- [ ] CSV import/export for core entities
- [ ] Data persistence across sessions

**Deferred to Phase 2:**
- [ ] Advanced Gantt features: dependencies, maintenance window overlays
- [ ] Advanced calculations: rig utilization, ETA, platform maintenance clash detection
- [ ] User authentication and roles enforcement
- [ ] Audit trail captures who/when/what before/after
- [ ] Scenario management and filtering by campaign(s)
- [ ] Excel import/export with advanced features

## Interfaces summary

Backend endpoints:
- [ ] /api/fields/ and /api/fields/{id}
- [ ] /api/platforms/ and /api/platforms/{id}
- [ ] /api/platforms/{id}/maintenance-windows and /api/maintenance-windows/{id}
- [ ] /api/rigs/ and /api/rigs/{id}
- [ ] /api/wells/ and /api/wells/{id}
- [ ] /api/projects/ and /api/projects/{id} (+ bulk)
- [ ] /api/campaigns/ and /api/campaigns/{id}
- [ ] /api/campaigns/{id}/projects
- [ ] /api/scenarios/ and /api/scenarios/clone
- [ ] /api/gantt
- [ ] /api/calc/run and /api/calc/{calc_run_id}
- [ ] /api/import and /api/export

Frontend routes (planned):
- [ ] /login
- [ ] /sheet
- [ ] /gantt
- [ ] /calc
- [ ] /import-export
- [ ] /map (optional)

## Notes

- Local dev authentication: session cookie and CSRF for simplicity; can swap to JWT later if needed.
- Visibility: keep this TODO evolving; add dates/owners when tasks start.
- Link back to spec for details: [docs/SPEC-002-Drilling Campaign Tracker.md](docs/SPEC-002-Drilling%20Campaign%20Tracker.md)

## Quick next actions (MVP Phase 1)

**Immediate Priority:**
- [x] Create repo structure
- [x] Bootstrap Django + DRF foundation
- [x] Scaffold React + Vite + TS with basic AG Grid
- [x] **NEXT: Create DRF serializers and ViewSets for all entities (M2)**
- [ ] **NEXT: Build API client and connect to real data (M3)**
- [ ] **NEXT: Implement comprehensive Projects sheet interface**

**Following Steps:**
- [ ] Add basic calculation engine with conflict detection
- [ ] Enhance Gantt view with real data integration
- [ ] Add CSV import/export functionality
- [ ] Test end-to-end workflows and polish UI

**Deferred:**
- [ ] Authentication and authorization system
- [ ] Audit trail implementation
- [ ] Advanced Gantt features and scenario management
