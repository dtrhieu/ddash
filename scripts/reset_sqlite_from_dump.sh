#!/usr/bin/env bash
set -euo pipefail

# Rebuild backend/db.sqlite3 from a dump directory of CSV/JSON files.
# Usage: scripts/reset_sqlite_from_dump.sh [dump_dir] [db_path]
# Defaults: scripts/dump_data/drilling_campaign_2025 backend/db.sqlite3

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
DUMP_DIR="${1:-$ROOT_DIR/scripts/dump_data/drilling_campaign_2025}"
DB_PATH="${2:-$ROOT_DIR/backend/db.sqlite3}"

echo "[reset] dump: $DUMP_DIR"
echo "[reset] db:   $DB_PATH"

# Remove existing DB
if [ -f "$DB_PATH" ]; then
  rm -f "$DB_PATH"
fi
mkdir -p "$(dirname "$DB_PATH")"

# Initialize from dump
python3 "$ROOT_DIR/scripts/init_sqlite_from_dump.py" --dump "$DUMP_DIR" --db "$DB_PATH" --force

echo "[reset] done"
