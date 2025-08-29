#!/usr/bin/env python3
"""
Initialize a SQLite database from a directory of CSV/JSON dump files.

Usage:
  python3 scripts/init_sqlite_from_dump.py --dump dump/drilling_campaign_2025 --db backend/db.sqlite3 --force

Behavior:
- Creates/overwrites the SQLite DB file (when --force is set) and creates one table per file.
- Supports .csv and .json (JSON array of objects). Columns inferred from headers/keys.
- All columns are created as TEXT to keep it simple and portable.
- If an "id" column exists, it is used as PRIMARY KEY; otherwise, an implicit rowid is kept.
- Existing tables with same name will be dropped when --force is specified; otherwise, script will skip existing tables.

This is schema-agnostic and intended for quick local data exploration and smoke testing.
"""

from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from pathlib import Path
from typing import Iterable


def infer_table_name(file_path: Path) -> str:
    # table name = file stem, lowercased, spaces/dashes to underscores
    return file_path.stem.strip().lower().replace(" ", "_").replace("-", "_")


def read_rows_from_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]


def read_rows_from_json(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        # allow {"items": [...]} style
        for k in ("items", "data", "results"):
            if k in data and isinstance(data[k], list):
                data = data[k]
                break
    if not isinstance(data, list):
        raise ValueError(f"JSON must be a list of objects: {path}")
    return [dict(x) for x in data]


def normalize_columns(rows: list[dict[str, object]]) -> list[str]:
    cols: set[str] = set()
    for r in rows:
        cols.update(str(k) for k in r.keys())
    # stable order
    return sorted(cols)


def coerce_text(val: object) -> str | None:
    if val is None:
        return None
    if isinstance(val, (str, int, float, bool)):
        return str(val)
    return json.dumps(val, ensure_ascii=False)


def ensure_table(
    conn: sqlite3.Connection,
    table: str,
    columns: Iterable[str],
    use_pk: bool,
    force: bool,
) -> None:
    cur = conn.cursor()
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
    )
    exists = cur.fetchone() is not None
    if exists:
        if force:
            cur.execute(f"DROP TABLE IF EXISTS {table}")
        else:
            return
    cols_def = []
    for c in columns:
        if use_pk and c == "id":
            cols_def.append("id TEXT PRIMARY KEY")
        else:
            cols_def.append(f"{c} TEXT")
    ddl = f"CREATE TABLE IF NOT EXISTS {table} (" + ", ".join(cols_def) + ")"
    cur.execute(ddl)
    conn.commit()


def insert_rows(
    conn: sqlite3.Connection,
    table: str,
    columns: list[str],
    rows: list[dict[str, object]],
) -> int:
    if not rows:
        return 0
    placeholders = ", ".join(["?"] * len(columns))
    sql = (
        f"INSERT OR REPLACE INTO {table} ("
        + ", ".join(columns)
        + f") VALUES ({placeholders})"
    )
    values = []
    for r in rows:
        values.append([coerce_text(r.get(c)) for c in columns])
    cur = conn.cursor()
    cur.executemany(sql, values)
    conn.commit()
    return cur.rowcount or 0


def load_file(conn: sqlite3.Connection, path: Path, force: bool) -> tuple[str, int]:
    table = infer_table_name(path)
    if path.suffix.lower() == ".csv":
        rows = read_rows_from_csv(path)
    elif path.suffix.lower() == ".json":
        rows = read_rows_from_json(path)
    else:
        return table, 0
    columns = normalize_columns(rows)
    use_pk = "id" in columns
    ensure_table(conn, table, columns, use_pk, force)
    inserted = insert_rows(conn, table, columns, rows)
    return table, inserted


def default_dump_dir() -> Path:
    # Default to repository's scripts/dump_data/drilling_campaign_2025
    return Path(__file__).resolve().parent / "dump_data" / "drilling_campaign_2025"


def iter_data_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".csv", ".json"}:
            files.append(p)
    return sorted(files)


def main() -> None:
    ap = argparse.ArgumentParser(description="Initialize SQLite DB from dump directory")
    ap.add_argument(
        "--dump",
        help=(
            "Path to directory with .csv/.json files (default: scripts/dump_data/drilling_campaign_2025)"
        ),
    )
    ap.add_argument(
        "--db", required=True, help="Path to SQLite database file to create/use"
    )
    ap.add_argument(
        "--force", action="store_true", help="Drop existing tables if present"
    )
    args = ap.parse_args()

    dump_dir = Path(args.dump) if args.dump else default_dump_dir()
    if not dump_dir.exists() or not dump_dir.is_dir():
        raise SystemExit(f"Dump directory not found: {dump_dir}")

    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    try:
        total = 0
        processed = 0
        for path in iter_data_files(dump_dir):
            table, n = load_file(conn, path, force=args.force)
            processed += 1
            total += n
            rel = (
                path.relative_to(dump_dir)
                if dump_dir in path.parents or path == dump_dir
                else path.name
            )
            print(f"Loaded {n} rows into '{table}' from {rel}")
        print(
            f"Done. Processed {processed} file(s). Inserted {total} row(s). DB: {db_path}"
        )
    finally:
        conn.close()


if __name__ == "__main__":
    main()
