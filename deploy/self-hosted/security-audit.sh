#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PYTHON="${AI_WORK_PYTHON:-$PROJECT_DIR/.venv/bin/python}"
AUDIT_CACHE_DIR="${AI_WORK_PIP_AUDIT_CACHE_DIR:-/tmp/ai-work-pip-audit-cache}"

fail() {
  printf 'ERROR: %s\n' "$1" >&2
  exit 1
}

[[ -x "$PYTHON" ]] || fail "Python environment not found: $PYTHON"
[[ -d "$PROJECT_DIR/tests" && -d "$PROJECT_DIR/.git" ]] || fail "Run this audit from a source checkout containing tests/ and .git/"
mkdir -p "$AUDIT_CACHE_DIR"

if ! "$PYTHON" -c 'import pip_audit, bandit' >/dev/null 2>&1; then
  fail "Security tools are missing. Run: $PYTHON -m pip install -r $PROJECT_DIR/requirements-security.txt"
fi

printf '\n[1/4] Python dependency vulnerability audit\n'
"$PYTHON" -m pip_audit --cache-dir "$AUDIT_CACHE_DIR" -r "$PROJECT_DIR/requirements.txt"

printf '\n[2/4] High-severity Python static security analysis\n'
"$PYTHON" -m bandit -q -r "$PROJECT_DIR/app" \
  --severity-level high --confidence-level high \
  -x "$PROJECT_DIR/app/__pycache__"

printf '\n[3/4] Tracked secret and private-key scan\n'
if git -C "$PROJECT_DIR" grep -nE \
  '(sk-[A-Za-z0-9_-]{20,}|AIza[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|xox[baprs]-[A-Za-z0-9-]{20,}|-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----)' \
  -- . ':(exclude)deploy/self-hosted/security-audit.sh'; then
  fail "Potential secret or private key found in tracked files"
fi
if [[ -n "$(git -C "$PROJECT_DIR" ls-files '*.env' '*.pem' '*.key')" ]]; then
  fail "Tracked environment or private-key file found"
fi
printf 'No tracked API keys or private keys matched the blocking patterns.\n'

printf '\n[4/4] Security regression tests\n'
cd "$PROJECT_DIR"
"$PYTHON" -m unittest \
  tests.test_security_hardening \
  tests.test_upload_security \
  tests.test_processing_jobs

printf '\nAutomated security audit passed.\n'
printf 'External vulnerability scanning and penetration testing still require an authorized target and test window.\n'
