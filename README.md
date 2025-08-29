# Drilling Campaign Tracker

Local-first MVP to plan and monitor drilling campaigns with a sheet-like UI, Gantt visualization, and a Python calc engine.

Source spec: docs/SPEC-002-Drilling Campaign Tracker.md

## Decisions (M0)
- Backend dependency tooling: pip-tools (requirements.in -> requirements.txt via pip-compile)
- Frontend package manager: npm
- Code quality:
  - Python: black, ruff, isort (via pre-commit)
  - TypeScript/JS: eslint, prettier (via pre-commit mirrors)

## Repo Layout (bootstrap)
- backend/ — Django + DRF (+ CORS) + calc placeholder (scaffolded in M1; Celery planned)
- frontend/ — React + Vite + TypeScript (scaffolded in M6)
- deploy/ — Dockerfiles, docker-compose, nginx (filled in M9)
- docs/ — additional docs and ADRs (optional, complement to existing doc/)

Planned key files (placeholders added where possible in M0):
- deploy/docker-compose.yml
- deploy/nginx.conf
- backend/pyproject.toml
- backend/manage.py
- backend/app/settings.py
- backend/app/urls.py
- backend/calc/engine.py
- frontend/index.html
- frontend/src/main.tsx
- frontend/src/pages/Gantt.tsx
- frontend/src/pages/Sheet.tsx

Spec: docs/SPEC-002-Drilling Campaign Tracker.md

## Getting Started (M0)
1) Ensure git is available; repo has been initialized via M0.
2) Install pre-commit (pipx or pip): pipx install pre-commit
3) Install git hooks: pre-commit install
4) Python toolchain is configured in backend/pyproject.toml.
5) Node is required for the frontend (already scaffolded). From repo root you can run:
   - npm run install:frontend
   - npm run dev | build | preview | lint (proxies to frontend/)

Next milestones:
- M1: Base apps and data model (pending)
- M6: Auth + API client + protected routes (in progress)
- M9: Compose & Nginx packaging (placeholders added)

## Current Progress
- Backend: Django + DRF + CORS configured; env-driven DB/Redis settings; health endpoint at `/api/health`; calc/engine placeholder functions.
- Frontend: Vite + React + TS + Tailwind; routing via React Router with Sidebar; Sheet page using AG Grid with demo data; Gantt wrapper around `frappe-gantt` with demo tasks.
- Deploy: `deploy/docker-compose.yml` and `deploy/nginx.conf` placeholders added for M9.

## Initialize SQLite DB from dump (schema-agnostic)
To create a throwaway SQLite database populated with the CSV dataset in `scripts/dump_data/drilling_campaign_2025` for ad‑hoc exploration:

- One-liner (rebuilds `backend/db.sqlite3`):
  - `scripts/reset_sqlite_from_dump.sh`

- Or run the Python loader directly (defaults to the folder above):
  - `python3 scripts/init_sqlite_from_dump.py --db backend/db.sqlite3 --force`
  - Pass a custom dump directory with `--dump /path/to/drilling_campaign_2025` if needed.

This creates one table per CSV (e.g., `fields`, `platforms`, `rigs`, `wells`, `projects`, `campaigns`, `campaign_projects`, `maintenance_windows`) with columns from the CSV headers (stored as TEXT). The `id` column, if present, is the PRIMARY KEY.

## Real app DB (Django schema + data)
For a database that matches Django models (FKs, constraints, indexes) and loads the CSVs via ORM:

- Clean rebuild and load from the built-in dump directory:
  - `scripts/bootstrap_real_db.sh`

- Or run commands manually:
  - `rm -f backend/db.sqlite3`
  - `python3 backend/manage.py migrate`
  - `python3 backend/manage.py load_dump --dump scripts/dump_data/drilling_campaign_2025`

Tips:
- You can export CREATE_SUPERUSER=1 to let the script create an admin user, or later run `python3 backend/manage.py createsuperuser`.
- Use `python3 backend/manage.py load_dump --dry-run` to validate without writing (transaction rollback).

## Frontend Dev (M6 skeleton)
- Prerequisites: Node.js >= 18, npm >= 8.
- Install deps:
  - From repo root: npm run install:frontend
  - Or: cd frontend && npm install
- Start dev server:
  - From repo root: npm run dev (proxies to frontend/)
  - Or: cd frontend && npm run dev
- Default URL: http://localhost:3000 (see frontend/vite.config.ts)
- Troubleshooting:
  - Module not found: 'frappe-gantt': run npm install in frontend. The dependency is declared in frontend/package.json.
  - CSS preprocessor error: [plugin:vite:css] Preprocessor dependency "sass-embedded" not found. Solution: run npm install in frontend (sass-embedded is declared as a devDependency). If it persists, delete frontend/node_modules and frontend/package-lock.json, then reinstall.
  - Port already in use: either stop the other service or run: npm --prefix frontend run dev -- --port 5173
  - Tailwind styles not applied: ensure postcss.config.js and tailwind.config.js exist (they do) and that src/index.css is imported (it is in src/main.tsx).
  - LAN access: server.host is true in vite.config.ts; access via your machine IP.
