#!/usr/bin/env bash
set -euo pipefail

CONFIG_FILE="/etc/ai-work/ai-work.env"
[[ -f "$CONFIG_FILE" ]] || { printf 'AI Work is not installed.\n' >&2; exit 1; }

systemctl status ai-work.service --no-pager
port="$(sed -n 's/^AI_WORK_HTTP_PORT=//p' "$CONFIG_FILE" | tail -n 1)"
curl --fail --silent --show-error "http://127.0.0.1:${port:-8000}/healthz"
printf '\n'
