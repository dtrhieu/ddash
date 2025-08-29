Drilling Campaign Tracker — Development Guidelines (Project‑specific)

Audience: advanced developers contributing to this repo. This file captures build/config specifics, testing workflow, and dev conventions that are particular to this project.

1) Backend build and configuration
- Runtime: Python 3.12, Django 5.2, DRF 3.15. SQLite by default for local dev; Postgres optional via env.
- Dependency management (pip-tools):
  - User installs should use the compiled lock files under backend/:
    - Production/dev runtime: pip install -r backend/requirements.txt
    - Dev tooling (pytest, ruff, pre-commit, pip-tools): pip install -r backend/requirements-dev.txt
  - If you must change dependencies: edit backend/requirements.in or requirements-dev.in and recompile with pip-compile (not needed for typical feature work).
- Django settings: backend/app/settings.py
  - Database selection is env-driven. Precedence:
    1) DATABASE_URL (postgres://user:pass@host:port/db)
    2) POSTGRES_HOST (+ POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_PORT)
    3) Fallback: SQLite file at backend/db.sqlite3
  - Caching: REDIS_URL enables RedisCache; otherwise defaults to LocMemCache.
  - CORS for Vite: http://localhost:5173 enabled.
- Common local workflow:
  - Migrations: python backend/manage.py migrate
  - Superuser (interactive): python backend/manage.py createsuperuser
  - Superuser (non-interactive): export DJANGO_SUPERUSER_USERNAME/EMAIL/PASSWORD then python backend/manage.py createsuperuser --noinput
  - Run dev server: python backend/manage.py runserver (ALLOWED_HOSTS includes localhost, 127.0.0.1, testserver)
- Seed data options:
  - Minimal JSON fixtures: python backend/manage.py loaddata backend/core/fixtures/initial_core.json backend/scheduling/fixtures/initial_scheduling.json
  - CSV demo dataset via custom command: python backend/manage.py load_dump --dump scripts/dump_data/drilling_campaign_2025
  - Smoke script (loads fixtures and validates constraints): python scripts/smoke_m12.py

2) Frontend shortcuts (from repo root)
- Proxy scripts in package.json delegate into frontend/:
  - Install deps: npm run install:frontend
  - Dev server: npm run dev
  - Build: npm run build
  - Preview: npm run preview
  - Lint: npm run lint
- Default Vite dev origin is http://localhost:5173; CORS is pre-wired in backend settings.

3) API surface that aids local testing
- Health: GET /api/health — DB-independent readiness JSON.
- Schema-lite: GET /api/schema-lite — DRF router enumeration without external schema libs; used by tests to assert endpoint count/shape.
- Minimal docs: GET /api/docs/ — simple HTML template listing endpoints (TemplateView based).
- Core resources (registered in DefaultRouter): /api/fields/, /api/platforms/, /api/rigs/, /api/wells/, /api/maintenance-windows/, /api/scenarios/, /api/projects/, /api/campaigns/, /api/campaign-projects/, /api/calc-runs/

4) Testing (pytest + pytest-django)
- Configuration: see pytest.ini at repo root
  - DJANGO_SETTINGS_MODULE=app.settings
  - pythonpath=backend (so manage.py sibling imports just work)
  - testpaths=backend/tests (only tests under that directory are collected by default)
  - Naming: files test_*.py or *_test.py; classes Test* or *Tests; functions test_*
  - Default addopts: -ra -q (adjust with -v locally if needed)
- How to run:
  - All tests: pytest
  - Verbose: pytest -v
  - Single file: pytest backend/tests/test_api_crud_and_lists.py -v
  - Single test: pytest backend/tests/test_api_crud_and_lists.py::test_list_endpoints_and_crud_field -v
- Database usage patterns:
  - Unit-style tests without DB can use plain functions/classes — no marker.
  - Django TestCase implies transaction per test method with automatic rollback; no explicit marker required.
  - For function-style tests that hit the DB, add @pytest.mark.django_db. If you call management commands that issue flush or need transactional behavior, use transaction=True (see test_api_crud_and_lists.py).
  - Fixtures loading inside tests is done with django.core.management.call_command('loaddata', ...). Prefer flushing explicitly (call_command('flush', interactive=False)) for deterministic runs when mutating global state.
- HTTP client:
  - For DRF API tests use rest_framework.test.APIClient for JSON convenience.
  - For plain Django views (like /api/docs/) rest_framework client also works; Django test Client is available if needed.
- Example patterns in this repo:
  - API and schema smoke: backend/tests/test_api_docs_and_schema.py covers /api/schema-lite and /api/docs/.
  - Serializer validation: backend/tests/test_serializers.py shows TestCase-based roundtrip and validation logic.
  - CRUD and list endpoints with fixture bootstrapping: backend/tests/test_api_crud_and_lists.py demonstrates end-to-end list/create/retrieve/update/delete with deterministic DB state and fixture sets.
- Demonstration of adding a new test (validated during preparation of this document):
  - Temporary example created at backend/tests/test_demo_junie_temp.py with a trivial assertion.
  - Ran pytest and verified collection/passing.
  - Removed the temporary file to keep the tree clean, as this document is the only artifact to be added by this task.
  - To replicate yourself:
    1) Create backend/tests/test_demo_local.py with:
       def test_demo_passes():
           assert 1 + 1 == 2
    2) Run: pytest -q
    3) Remove the demo file after verifying.

5) Adding new tests — quick guidance
- Location: place backend tests under backend/tests/. Keep unit tests close to subject under apps when it materially improves locality, but ensure they’re discoverable via testpaths or use -k/-p options (default setup assumes backend/tests/).
- Style:
  - Prefer pytest functional style for API and serializer behaviors; use Django TestCase where setUp/tearDown and class isolation is useful.
  - Mark DB needs explicitly with @pytest.mark.django_db for function tests; prefer TestCase for model/serializer tests that can benefit from its isolation.
  - Keep API payloads minimal and assert both status codes and essential shape/keys.
- Determinism:
  - If tests modify global DB state, flush and reload fixtures per test or per class to avoid cross-test coupling (see test_api_crud_and_lists.py).
  - Avoid relying on implicit ordering; assert on content, not sequence, unless order is explicitly part of the behavior.

6) Code quality and conventions (backend)
- Lint/format: ruff configured in backend/pyproject.toml
  - Lint rules: E, F, I (isort), UP, B, SIM; target Python 3.12, line length 100, double quotes enforced.
  - Excludes migrations from lint.
- Pre-commit: repository expects pre-commit to be installed and hooks set up:
  - pipx install pre-commit (or pip install pre-commit)
  - pre-commit install
  - Hooks cover Python (ruff/black/isort mirrors) and frontend (eslint/prettier mirrors), as noted in README.
- DB model guidance:
  - SQLite is acceptable for local tests; Postgres features (e.g., GIN index) should be guarded by conditional migrations and tested behind feature detection.
  - Use explicit unique constraints and indexes as described in TODO.md. Composite indexes on scheduling.Project are already present.

7) Useful scripts and flows
- scripts/smoke_m12.py — sets up Django, loads initial fixtures, verifies maintenance overlap and basic links, and pings /api/health. Good for quick local sanity after DB or model changes.
- README contains end-to-end DB bootstrap instructions for both SQLite-from-CSV and real Django schema + fixtures. Prefer the "Real app DB" path for test-driven backend work.

8) Troubleshooting notes (test/dev)
- Tests fail with missing fixtures: ensure backend/core/fixtures/initial_core.json and backend/scheduling/fixtures/initial_scheduling.json exist and are accessible; they are committed to the repo.
- Settings not picked up in pytest: run from repo root (pytest.ini lives there and sets pythonpath/backend). Otherwise pass -c pytest.ini.
- Port conflicts on frontend dev: run npm --prefix frontend run dev -- --port 5173 or adjust vite config; backend CORS list already includes localhost:5173.
- Intermittent DB state: prefer flush + loaddata per test module/class when performing CRUD that depends on specific initial records.

9) Minimal local bring-up checklist
- Backend:
  - python -m venv backend/.venv && source backend/.venv/bin/activate
  - pip install -r backend/requirements-dev.txt
  - python backend/manage.py migrate
  - python backend/manage.py loaddata backend/core/fixtures/initial_core.json backend/scheduling/fixtures/initial_scheduling.json
  - python backend/manage.py runserver
- Frontend:
  - npm run install:frontend
  - npm run dev
- Tests:
  - pytest -q (expect all green)

Status note for this document
- All instructions above were validated against the current tree:
