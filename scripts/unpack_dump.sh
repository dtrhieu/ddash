#!/usr/bin/env bash
set -euo pipefail
# Unpack a dump zip into dump/<name>
# Usage: scripts/unpack_dump.sh scripts/dump_data/drilling_campaign_2025.zip

ZIP_PATH="$1"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
DUMP_DIR="$ROOT_DIR/dump"
mkdir -p "$DUMP_DIR"

name=$(basename "$ZIP_PATH" .zip)
out_dir="$DUMP_DIR/$name"
rm -rf "$out_dir"
mkdir -p "$out_dir"

unzip -o "$ZIP_PATH" -d "$out_dir" >/dev/null

echo "Unpacked to: $out_dir"
