#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"
COMPOSE_FILE="$SCRIPT_DIR/compose.yml"
BACKUP_DIR="$ROOT_DIR/backups"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
ARCHIVE="$BACKUP_DIR/ai-work-$STAMP.tar.gz"

[[ -f "$ENV_FILE" ]] || { printf 'Run install.sh first.\n' >&2; exit 1; }
mkdir -p "$BACKUP_DIR"

cd "$SCRIPT_DIR"
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" stop ai-work
trap 'docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" start ai-work >/dev/null' EXIT

tar -C "$ROOT_DIR" -czf "$ARCHIVE" data storage mock_nas deploy/self-hosted/.env
chmod 600 "$ARCHIVE"
printf 'Backup created: %s\n' "$ARCHIVE"
