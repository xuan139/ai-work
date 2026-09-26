#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

[[ "${EUID:-$(id -u)}" == "0" ]] || { printf 'Run this script with sudo.\n' >&2; exit 1; }
[[ -f /etc/ai-work/ai-work.env ]] || { printf 'AI Work is not installed.\n' >&2; exit 1; }

"$SCRIPT_DIR/backup.sh"
exec "$SCRIPT_DIR/install.sh"
