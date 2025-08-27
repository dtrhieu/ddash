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
