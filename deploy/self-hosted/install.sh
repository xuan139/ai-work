#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
INSTALL_DIR="/opt/ai-work"
STATE_DIR="/var/lib/ai-work"
CONFIG_DIR="/etc/ai-work"
CONFIG_FILE="$CONFIG_DIR/ai-work.env"
SERVICE_FILE="/etc/systemd/system/ai-work.service"

fail() {
  printf 'ERROR: %s\n' "$1" >&2
  exit 1
}

[[ "$(uname -s)" == "Linux" ]] || fail "This installer supports Ubuntu Linux only."
[[ "${EUID:-$(id -u)}" == "0" ]] || fail "Run this installer with sudo."
command -v apt-get >/dev/null 2>&1 || fail "apt-get was not found; Ubuntu 22.04 or 24.04 is required."

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends \
  python3 python3-venv python3-pip ffmpeg curl ca-certificates openssl

if ! id aiwork >/dev/null 2>&1; then
  useradd --system --home-dir "$STATE_DIR" --create-home --shell /usr/sbin/nologin aiwork
fi

systemctl stop ai-work.service 2>/dev/null || true

install -d -o root -g root -m 0755 "$INSTALL_DIR"
install -d -o aiwork -g aiwork -m 0750 \
  "$STATE_DIR/data" \
  "$STATE_DIR/storage" \
  "$STATE_DIR/mock_nas/inbox" \
  "$STATE_DIR/mock_nas/processed"
install -d -o root -g aiwork -m 0750 "$CONFIG_DIR"

rm -rf "$INSTALL_DIR/app" "$INSTALL_DIR/static" "$INSTALL_DIR/deploy" "$INSTALL_DIR/docs"
install -d -o root -g root -m 0755 "$INSTALL_DIR/deploy"
cp -a "$SOURCE_DIR/app" "$SOURCE_DIR/static" "$SOURCE_DIR/docs" "$INSTALL_DIR/"
cp -a "$SOURCE_DIR/deploy/self-hosted" "$INSTALL_DIR/deploy/"
cp -a "$SOURCE_DIR/deploy/nginx-ai-work-upload.conf" "$SOURCE_DIR/deploy/ai-work-embedding.service" "$INSTALL_DIR/deploy/"
cp -a "$SOURCE_DIR"/requirements*.txt "$SOURCE_DIR/README.md" "$SOURCE_DIR/LICENSE" "$SOURCE_DIR/VERSION" "$INSTALL_DIR/"

rm -rf "$INSTALL_DIR/data" "$INSTALL_DIR/storage" "$INSTALL_DIR/mock_nas"
ln -s "$STATE_DIR/data" "$INSTALL_DIR/data"
ln -s "$STATE_DIR/storage" "$INSTALL_DIR/storage"
ln -s "$STATE_DIR/mock_nas" "$INSTALL_DIR/mock_nas"

if [[ ! -d "$INSTALL_DIR/.venv" ]]; then
  python3 -m venv "$INSTALL_DIR/.venv"
fi
"$INSTALL_DIR/.venv/bin/python" -m pip install --upgrade pip wheel
"$INSTALL_DIR/.venv/bin/python" -m pip install -r "$INSTALL_DIR/requirements.txt"

package_version="$(tr -d '[:space:]' < "$SOURCE_DIR/VERSION" 2>/dev/null || true)"
package_version="${package_version:-development}"
if [[ ! -f "$CONFIG_FILE" ]]; then
  umask 077
  secret_key="$(openssl rand -hex 32)"
  admin_password="$(openssl rand -base64 24 | tr -d '=+/\n' | cut -c1-24)"
  primary_ip="$(hostname -I 2>/dev/null | awk '{print $1}')"
  public_url="${AI_WORK_PUBLIC_URL:-http://${primary_ip:-localhost}:8000}"

  sed \
    -e "s|^AI_WORK_VERSION=.*|AI_WORK_VERSION=$package_version|" \
    -e "s|^APP_SECRET_KEY=.*|APP_SECRET_KEY=$secret_key|" \
    -e "s|^AI_WORK_ADMIN_PASSWORD=.*|AI_WORK_ADMIN_PASSWORD=$admin_password|" \
    -e "s|^AI_WORK_PUBLIC_URL=.*|AI_WORK_PUBLIC_URL=$public_url|" \
    "$SCRIPT_DIR/.env.example" > "$CONFIG_FILE"
  chmod 0640 "$CONFIG_FILE"
  chown root:aiwork "$CONFIG_FILE"
  credentials_created=1
else
  sed -i "s|^AI_WORK_VERSION=.*|AI_WORK_VERSION=$package_version|" "$CONFIG_FILE"
  credentials_created=0
  public_url="$(sed -n 's/^AI_WORK_PUBLIC_URL=//p' "$CONFIG_FILE" | tail -n 1)"
fi

chown -R root:root "$INSTALL_DIR/app" "$INSTALL_DIR/static" "$INSTALL_DIR/deploy" "$INSTALL_DIR/docs"
chown -R root:root "$INSTALL_DIR/.venv"
install -o root -g root -m 0644 "$SCRIPT_DIR/ai-work.service" "$SERVICE_FILE"

systemctl daemon-reload
systemctl enable --now ai-work.service

port="$(sed -n 's/^AI_WORK_HTTP_PORT=//p' "$CONFIG_FILE" | tail -n 1)"
port="${port:-8000}"
printf 'Waiting for AI Work Core on port %s' "$port"
for _ in $(seq 1 40); do
  if curl --fail --silent "http://127.0.0.1:${port}/healthz" >/dev/null; then
    printf '\nAI Work Core is ready: %s\n' "${public_url:-http://localhost:$port}"
    if [[ "$credentials_created" == "1" ]]; then
      printf 'Initial username: admin\n'
      printf 'Initial password: %s\n' "$admin_password"
      printf 'Change the password immediately after the first login.\n'
    fi
    exit 0
  fi
  printf '.'
  sleep 3
done

printf '\nAI Work did not become healthy. Recent logs:\n' >&2
journalctl -u ai-work.service -n 100 --no-pager >&2
exit 1
