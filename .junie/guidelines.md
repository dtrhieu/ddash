Drilling Campaign Tracker — Development Guidelines

Context snapshot
- Backend: Python 3.12, Django/DRF/Celery planned, but not scaffolded yet (placeholders in backend/app/* and manage.py). Pure calc utilities exist in backend/calc/engine.py.
- Frontend: React + Vite + TypeScript planned; skeleton files exist under frontend/ but no build tooling wired yet.
- Tooling decisions (from README):
  - Python: black, ruff, isort via pre-commit
  - JS/TS: eslint, prettier via pre-commit mirrors
  - Dependency mgmt for Python: pip-tools (requirements.in/lock via pip-compile) — to be introduced in later milestones.
- Deploy: docker-compose and nginx stubs exist in deploy/.

Build and configuration
1) Python toolchain (backend)
- Version: Python 3.12 (see backend/pyproject.toml configuration for tools).
- Virtualenv: optional for now; there are no runtime dependencies yet. If you set up one, use Python 3.12 to avoid tooling mismatches.
- Code style tools configured in pyproject:
  - black (line-length 100), isort (profile black), ruff (E, F, I, UP, B, SIM). These are intended to run via pre-commit.
- Pre-commit hooks:
  - Install: pipx install pre-commit (or pip install pre-commit)
  - Activate: pre-commit install
  - Run manually: pre-commit run -a

2) Frontend toolchain
- Skeleton only; Node will be needed in a later milestone (M6). No install/build required at this stage.

3) Namespace package layout note
- The backend directory uses Python implicit namespace packages (no __init__.py). This is intentional to keep the bootstrap minimal. It affects test discovery (see Testing section) and import mechanics when running modules.

Testing
At this milestone we can test pure functions in backend/calc/engine.py without Django. Prefer Python’s built-in unittest to avoid new dependencies.

Quick start: running tests
- Module-based invocation (works with implicit namespace packages):
  python3 -m unittest backend.tests.test_engine -v

- Discovery invocation can miss tests because tests/ is not a package. If you want discovery:
  - Option A (recommended later): add __init__.py to backend and backend/tests to make them packages; then run:
      python3 -m unittest discover -s backend -p 'test_*.py' -v
    Note: This changes package semantics for the repo; avoid until the team agrees.
  - Option B: keep module-based invocation (above) for now.

Adding tests
- Location: place tests under backend/tests/ with filenames test_*.py.
- Imports: import from backend.calc.engine since backend is a namespace package.
- Example template:
  # backend/tests/test_engine_example.py
  import unittest
  from datetime import date
  from backend.calc.engine import compute_duration

  class TestEngineExample(unittest.TestCase):
      def test_duration(self):
          self.assertEqual(compute_duration(date(2025, 1, 1), date(2025, 1, 11)), 10)

  if __name__ == '__main__':
      unittest.main()

- Run (module target):
  python3 -m unittest backend.tests.test_engine_example -v

What we validated
- We created and successfully executed a sample test file for backend/calc/engine.py using the module-based runner. The test covered:
  - compute_duration (normal and end-before-start cases)
  - compute_npt_pct (bounds and zero-duration behavior)
  - compute_costs (base + extras and non-negative guards)
  - estimate_eta (max date and empty input)
  - run_all_metrics placeholder contract (ok flag and metrics key)
- The test suite passed under Python 3.12 with no external dependencies.

Guidelines for future test expansion
- Keep tests pure for backend/calc until Django is scaffolded (M1+). Avoid mocking Django unless the project structure is promoted to a real Django app.
- Prefer deterministic inputs and avoid timezone/date coupling; use datetime.date for calc functions.
- Maintain tests close to the domain (doc/SPEC-002-Drilling Campaign Tracker.md) and encode edge cases found in the spec.

Code quality and conventions
- Python
  - Formatting: black (line length 100)
  - Imports: isort (profile black)
  - Linting: ruff (E, F, I, UP, B, SIM enabled)
  - Typing: code uses modern typing (from __future__ import annotations). Preserve annotations on new functions.
  - Namespaces: prefer flat modules for pure calc; keep side-effect-free imports (no I/O, no network) in calc layer.

- JavaScript/TypeScript (planned)
  - ESLint + Prettier via pre-commit mirrors when frontend is scaffolded in M6. Until then, no npm/node steps are required.

Local dev workflow tips
- Keep backend and frontend decoupled until API contracts stabilize. For calc changes, only touch backend/calc/* and tests under backend/tests/.
- When upgrading tooling, ensure pre-commit hooks still run on Python 3.12 and that ruff/black versions remain compatible with pyproject settings.
- If adding pytest later, set testpaths = ["backend/tests"] and pythonpath to project root, or add a minimal conftest.py; but avoid introducing new deps until the milestone plans call for it.

Troubleshooting
- ImportError for backend.calc.engine during tests:
  - Ensure you run from the repo root, and use module-based unittest invocation (python3 -m unittest backend.tests.test_... ). This leverages implicit namespace packages.
- NO TESTS RAN using discover:
  - This is expected without package __init__.py files. Use module-based invocation or convert tests dir into a package.

Changelog for this guideline file
- 2025-08-27: Initial guidelines, validated sample unittest for calc engine, documented namespace/discovery caveats and dev tooling configuration.
- 2025-08-27: Updated Python version references to 3.12 and aligned tool target versions.
