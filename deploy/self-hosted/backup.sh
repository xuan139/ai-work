#!/usr/bin/env bash
set -euo pipefail

STATE_DIR="/var/lib/ai-work"
CONFIG_DIR="/etc/ai-work"
BACKUP_DIR="/var/backups/ai-work"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
ARCHIVE="$BACKUP_DIR/ai-work-$STAMP.tar.gz"

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

tar -C / -czf "$ARCHIVE" var/lib/ai-work etc/ai-work
chmod 0600 "$ARCHIVE"
printf 'Backup created: %s\n' "$ARCHIVE"
