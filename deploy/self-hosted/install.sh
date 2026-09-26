#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"
COMPOSE_FILE="$SCRIPT_DIR/compose.yml"

fail() {
  printf 'ERROR: %s\n' "$1" >&2
  exit 1
}

command -v docker >/dev/null 2>&1 || fail "Docker Engine is required. Install Docker Engine and the Compose plugin first."
docker compose version >/dev/null 2>&1 || fail "Docker Compose v2 is required."
command -v openssl >/dev/null 2>&1 || fail "openssl is required to generate installation secrets."

mkdir -p "$ROOT_DIR/data" "$ROOT_DIR/storage" "$ROOT_DIR/mock_nas/inbox" "$ROOT_DIR/mock_nas/processed"

if [[ ! -f "$ENV_FILE" ]]; then
  umask 077
  package_version="$(tr -d '[:space:]' < "$ROOT_DIR/VERSION" 2>/dev/null || true)"
  package_version="${package_version:-development}"
  secret_key="$(openssl rand -hex 32)"
  admin_password="$(openssl rand -base64 24 | tr -d '=+/\n' | cut -c1-24)"
  public_url="${AI_WORK_PUBLIC_URL:-http://$(hostname -I 2>/dev/null | awk '{print $1}'):8000}"
  [[ "$public_url" != "http://:8000" ]] || public_url="http://localhost:8000"

  sed \
    -e "s|^AI_WORK_VERSION=.*|AI_WORK_VERSION=$package_version|" \
    -e "s|^APP_SECRET_KEY=.*|APP_SECRET_KEY=$secret_key|" \
    -e "s|^AI_WORK_ADMIN_PASSWORD=.*|AI_WORK_ADMIN_PASSWORD=$admin_password|" \
    -e "s|^AI_WORK_UID=.*|AI_WORK_UID=$(id -u)|" \
    -e "s|^AI_WORK_GID=.*|AI_WORK_GID=$(id -g)|" \
    -e "s|^AI_WORK_PUBLIC_URL=.*|AI_WORK_PUBLIC_URL=$public_url|" \
    "$SCRIPT_DIR/.env.example" > "$ENV_FILE"
  chmod 600 "$ENV_FILE"
  credentials_created=1
else
  credentials_created=0
fi

cd "$SCRIPT_DIR"
if ! docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" pull ai-work; then
  printf 'Published image is unavailable; building the image from this package.\n'
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" build ai-work
fi
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d ai-work

port="$(sed -n 's/^AI_WORK_HTTP_PORT=//p' "$ENV_FILE" | tail -n 1)"
port="${port:-8000}"
printf 'Waiting for AI Work Core on port %s' "$port"
for _ in $(seq 1 40); do
  if curl --fail --silent "http://127.0.0.1:${port}/healthz" >/dev/null; then
    printf '\nAI Work Core is ready: http://127.0.0.1:%s\n' "$port"
    if [[ "$credentials_created" == "1" ]]; then
      printf 'Initial username: admin\n'
      printf 'Initial password: %s\n' "$admin_password"
      printf 'Change the password after the first login. The generated value is also stored in %s.\n' "$ENV_FILE"
    fi
    exit 0
  fi
  printf '.'
  sleep 3
done

printf '\nAI Work did not become healthy. Recent logs:\n' >&2
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" logs --tail=100 ai-work >&2
exit 1
