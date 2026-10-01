#!/usr/bin/env bash
set -uo pipefail

CONFIG_FILE="${AI_WORK_CONFIG_FILE:-/etc/ai-work/ai-work.env}"
failures=0

pass() { printf 'PASS  %s\n' "$1"; }
fail() { printf 'FAIL  %s\n' "$1"; failures=$((failures + 1)); }

config_value() {
  sed -n "s/^$1=//p" "$CONFIG_FILE" | tail -n 1
}

[[ -r "$CONFIG_FILE" ]] || { fail "Cannot read $CONFIG_FILE"; exit 1; }

environment="$(config_value AI_WORK_ENV)"
public_url="$(config_value AI_WORK_PUBLIC_URL)"
bind_host="$(config_value AI_WORK_BIND_HOST)"
secret="$(config_value APP_SECRET_KEY)"
admin_password="$(config_value AI_WORK_ADMIN_PASSWORD)"

[[ "$environment" == "production" ]] && pass "Production mode is enabled" || fail "AI_WORK_ENV must be production"
[[ "$public_url" == https://* ]] && pass "Public URL uses HTTPS" || fail "AI_WORK_PUBLIC_URL must use HTTPS"
[[ "$bind_host" == "127.0.0.1" || "$bind_host" == "::1" ]] && pass "FastAPI is bound to loopback" || fail "AI_WORK_BIND_HOST must be loopback"
[[ ${#secret} -ge 32 && "$secret" != replace-* ]] && pass "Application secret is configured" || fail "APP_SECRET_KEY is weak or unset"
[[ ${#admin_password} -ge 12 && "$admin_password" != "admin123" && "$admin_password" != replace-* ]] && pass "Initial admin password is non-default" || fail "AI_WORK_ADMIN_PASSWORD is weak or default"

config_mode="$(stat -c '%a' "$CONFIG_FILE" 2>/dev/null || true)"
config_owner="$(stat -c '%U:%G' "$CONFIG_FILE" 2>/dev/null || true)"
[[ "$config_mode" == "640" || "$config_mode" == "600" ]] && pass "Configuration permissions are restricted" || fail "Configuration mode must be 0640 or 0600"
[[ "$config_owner" == "root:aiwork" || "$config_owner" == "root:root" ]] && pass "Configuration owner is restricted" || fail "Configuration owner must be root:aiwork or root:root"

if command -v systemctl >/dev/null 2>&1 && systemctl is-active --quiet ai-work.service; then
  pass "ai-work.service is active"
else
  fail "ai-work.service is not active"
fi

if curl --fail --silent --show-error --max-time 15 "$public_url/healthz" >/dev/null 2>&1; then
  pass "Public health endpoint is reachable"
else
  fail "Public health endpoint is not reachable"
fi

if curl --fail --silent --show-error --max-time 15 -I "$public_url/" 2>/dev/null | tr -d '\r' | grep -qi '^strict-transport-security:'; then
  pass "HSTS response header is present"
else
  fail "HSTS response header is missing"
fi

printf '\nSecurity preflight completed with %d failure(s).\n' "$failures"
exit "$failures"
