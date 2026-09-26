#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"
COMPOSE_FILE="$SCRIPT_DIR/compose.yml"

[[ -f "$ENV_FILE" ]] || { printf 'Run install.sh first.\n' >&2; exit 1; }
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps
port="$(sed -n 's/^AI_WORK_HTTP_PORT=//p' "$ENV_FILE" | tail -n 1)"
curl --fail --silent --show-error "http://127.0.0.1:${port:-8000}/healthz"
printf '\n'
