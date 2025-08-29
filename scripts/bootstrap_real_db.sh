#!/usr/bin/env bash
set -euo pipefail
# Scaffold Django schema and load CSV dump via ORM (real app DB)
# Usage: scripts/bootstrap_real_db.sh [dump_dir]

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
DUMP_DIR="${1:-$ROOT_DIR/scripts/dump_data/drilling_campaign_2025}"
DB_PATH="$ROOT_DIR/backend/db.sqlite3"

echo "[realdb] removing existing DB: $DB_PATH"
rm -f "$DB_PATH"

pushd "$ROOT_DIR/backend" >/dev/null

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    echo "[realdb] activating virtual environment"
    source .venv/bin/activate
else
    echo "[realdb] warning: virtual environment not found at .venv/bin/activate"
fi

python3 manage.py migrate
python3 manage.py load_dump --dump "$DUMP_DIR" ${DRY_RUN:+--dry-run} ${CREATE_SUPERUSER:+--create-superuser} || true
popd >/dev/null

echo "[realdb] done: $DB_PATH"
