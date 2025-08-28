# Drilling Campaign Tracker

Local-first MVP to plan and monitor drilling campaigns with a sheet-like UI, Gantt visualization, and a Python calc engine.

Source spec: doc/SPEC-002-Drilling Campaign Tracker.md

## Decisions (M0)
- Backend dependency tooling: pip-tools (requirements.in -> requirements.txt via pip-compile)
- Frontend package manager: npm
- Code quality:
  - Python: black, ruff, isort (via pre-commit)
  - TypeScript/JS: eslint, prettier (via pre-commit mirrors)

## Repo layout (bootstrap)
- backend/ — Django + DRF + Celery + calc (scaffolded in M1)
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

Spec: doc/SPEC-002-Drilling Campaign Tracker.md

## Getting started (M0)
1) Ensure git is available; repo has been initialized via M0.
2) Install pre-commit (pipx or pip): pipx install pre-commit
3) Install git hooks: pre-commit install
4) Python toolchain is configured in backend/pyproject.toml (no runtime deps yet).
5) ESLint/Prettier hooks are configured via mirrors; Node will be required when we scaffold the frontend in M6.

Next milestones:
- M1: Bootstrap Django + DRF + base apps and settings
- M6: Scaffold React + Vite + TS and baseline routes/components
- M9: Compose & Nginx packaging for local

## Frontend dev (M6 skeleton)
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
