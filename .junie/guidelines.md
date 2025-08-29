Drilling Campaign Tracker — Development Guidelines

Context snapshot
- Backend: Python 3.12. Django/DRF are scaffolded; minimal project exists with health endpoint and env-driven settings. Domain apps and APIs for M1.2–M3 are pending implementation. Pure calc utilities exist in backend/calc/engine.py.
- Frontend: React + Vite + TypeScript scaffold present; basic Sheet and Gantt pages exist but are not wired to a backend API.
- Tooling decisions (from README):
  - Python: ruff (lint) + ruff-format (format) via pre-commit; import sorting via Ruff's isort rules
  - JS/TS: eslint via pre-commit mirror (no Prettier configured)
  - Dependency mgmt for Python: pip-tools (requirements.in/lock via pip-compile)
- Deploy: docker-compose and nginx stubs exist in deploy/.

Build and configuration
1) Python toolchain (backend)
- Version: Python 3.12 (see backend/pyproject.toml configuration for tools).
- Virtualenv: optional for now. If you set up one, use Python 3.12 to avoid tooling mismatches.
- Code style tools configured in pyproject:
  - ruff (lint: E, F, I, UP, B, SIM) + ruff-format (format, line-length 100). Import sorting via Ruff's isort rules. Run via pre-commit.
- Pre-commit hooks:
  - Install: pipx install pre-commit (or pip install pre-commit)
  - Activate: pre-commit install
  - Run manually: pre-commit run -a

2) Frontend toolchain
- Skeleton only; Node will be needed in M6+. No install/build required for M1.2–M3.

3) Namespace package layout note
- The backend directory uses Python implicit namespace packages (no __init__.py). This affects test discovery (see Testing) and imports.

Testing
- For M1.2–M3, prioritize unit tests for pure calc and minimal Django model validation where feasible, using Python’s built-in unittest. Avoid introducing pytest for now.

Quick start: running tests
- Module-based invocation (works with implicit namespace packages):
  python3 -m unittest backend.tests.test_engine -v

- Discovery can miss tests because tests/ is not a package. If you want discovery later, convert to packages first.

Adding tests
- Location: backend/tests/ with filenames test_*.py.
- Imports: import from backend.calc.engine or from Django apps using the fully-qualified path (e.g., backend.users.models) once created.
- Example template remains the same as before.

Milestone-specific guidance (this task)
- M1.2 (Base apps and data model):
  - Create Django apps: users, core, scheduling, calc (models-only for calc). Keep apps minimal (apps.py, models.py, admin.py).
  - Implement models per spec with clear enums and indexes. Prefer PostgreSQL-friendly fields but keep SQLite compatibility for local dev.
  - Add initial migrations; do not add business logic beyond field constraints.
  - Register models in admin for visibility. Seed minimal fixtures if time allows.
- M2 (AuthZ and Audit):
  - Use Django’s session auth locally. Define role choices on User (Viewer, Editor, Admin) and basic DRF permission classes mapping to roles.
  - Implement AuditLog via model signals capturing before/after snapshots for create/update/delete with user attribution where available.
- M3 (Core APIs):
  - Implement read/write DRF viewsets for core entities with list/retrieve/create/update/destroy. Add basic filtering, pagination, and validation hooks.
  - Keep permissions simple: Viewer = read-only; Editor/Admin = write.

Code quality and conventions
- Python
  - Formatting: ruff-format (line length 100)
  - Imports: sorted by Ruff's isort rules (no separate isort invocation)
  - Linting: ruff (E, F, I, UP, B, SIM enabled)
  - Typing: use modern typing (from __future__ import annotations). Preserve annotations on new functions and models.
  - Namespaces: prefer flat modules for pure calc; keep side-effect-free imports in calc.

- JavaScript/TypeScript
  - ESLint via pre-commit mirror (no Prettier configured). No additional node steps needed for M1.2–M3.

Local dev workflow tips
- Keep backend and frontend decoupled until API contracts stabilize. For calc changes, only touch backend/calc/* and tests under backend/tests/.
- When upgrading tooling, ensure pre-commit hooks still run on Python 3.12 and that ruff/ruff-format versions remain compatible with pyproject settings.

Troubleshooting
- ImportError for backend.calc.engine during tests:
  - Run from the repo root, and use module-based unittest invocation.
- NO TESTS RAN using discover:
  - Expected without package __init__.py. Use module invocation or convert tests dir into a package.

Changelog for this guideline file
- 2025-08-27: Initial guidelines, validated sample unittest for calc engine, documented namespace/discovery caveats and dev tooling configuration.
- 2025-08-27: Updated Python version references to 3.12 and aligned tool target versions.
- 2025-08-28: Updated context snapshot per TODO/SPEC: backend minimal Django scaffolding exists; frontend Sheet/Gantt scaffolds present.
- 2025-08-29: Updated to include M1.2–M3 execution guidance for this task.
- 2025-08-29: Aligned with .pre-commit-config — switched to Ruff + Ruff-Format for Python (no Black/Isort hooks); ESLint only for JS/TS (no Prettier).
