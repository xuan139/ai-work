#!/usr/bin/env bash
set -euo pipefail

STATE_DIR="/var/lib/ai-work"
CONFIG_DIR="/etc/ai-work"
BACKUP_DIR="/var/backups/ai-work"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
PLAIN_ARCHIVE="$BACKUP_DIR/ai-work-$STAMP.tar.gz"
ARCHIVE="$PLAIN_ARCHIVE"

[[ "${EUID:-$(id -u)}" == "0" ]] || { printf 'Run this script with sudo.\n' >&2; exit 1; }
[[ -d "$STATE_DIR" && -f "$CONFIG_DIR/ai-work.env" ]] || { printf 'AI Work is not installed.\n' >&2; exit 1; }

install -d -o root -g root -m 0700 "$BACKUP_DIR"
was_active=0
if systemctl is-active --quiet ai-work.service; then
  was_active=1
  systemctl stop ai-work.service
fi
restore_service() {
  if [[ "$was_active" == "1" ]]; then
    systemctl start ai-work.service
  fi
}
trap restore_service EXIT

tar -C / -czf "$PLAIN_ARCHIVE" var/lib/ai-work etc/ai-work
tar -tzf "$PLAIN_ARCHIVE" >/dev/null
passphrase_file="${AI_WORK_BACKUP_PASSPHRASE_FILE:-}"
if [[ -n "$passphrase_file" ]]; then
  [[ -f "$passphrase_file" ]] || { printf 'Backup passphrase file not found: %s\n' "$passphrase_file" >&2; exit 1; }
  ARCHIVE="$PLAIN_ARCHIVE.enc"
  openssl enc -aes-256-cbc -salt -pbkdf2 -iter 200000 \
    -pass "file:$passphrase_file" -in "$PLAIN_ARCHIVE" -out "$ARCHIVE"
  rm -f "$PLAIN_ARCHIVE"
fi
chmod 0600 "$ARCHIVE"
printf 'Backup created: %s\n' "$ARCHIVE"
