#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"
COMPOSE_FILE="$SCRIPT_DIR/compose.yml"

[[ -f "$ENV_FILE" ]] || { printf 'Run install.sh first.\n' >&2; exit 1; }

"$SCRIPT_DIR/backup.sh"

cd "$SCRIPT_DIR"
if ! docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" pull ai-work; then
  printf 'Published image is unavailable; rebuilding from the local package.\n'
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" build --pull ai-work
fi
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d ai-work
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps
