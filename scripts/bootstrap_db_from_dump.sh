#!/usr/bin/env bash
set -euo pipefail
# Convenience script: unpack built-in dump zip and build SQLite DB from it.
# Usage: scripts/bootstrap_db_from_dump.sh [zip_path] [db_path]

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
ZIP_PATH="${1:-$ROOT_DIR/scripts/dump_data/drilling_campaign_2025.zip}"
DB_PATH="${2:-$ROOT_DIR/backend/db.sqlite3}"

"$ROOT_DIR/scripts/unpack_dump.sh" "$ZIP_PATH"
DUMP_DIR="$ROOT_DIR/dump/$(basename "$ZIP_PATH" .zip)"
"$ROOT_DIR/scripts/reset_sqlite_from_dump.sh" "$DUMP_DIR" "$DB_PATH"

echo "Bootstrap complete: $DB_PATH"
