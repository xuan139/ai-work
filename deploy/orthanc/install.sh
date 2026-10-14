#!/usr/bin/env bash
set -euo pipefail

# Run only on the approved Ubuntu deployment host, after backing up the portal.
ROOT=/home/ubuntu/ai-work
cd "$ROOT"
test "$(uname -s)" = Linux
test "$(uname -m)" = x86_64
test "$(id -un)" = ubuntu
test -x .venv/bin/python
sudo -n true
if systemctl is-active --quiet aiwork-orthanc.service; then
  echo 'Dedicated Orthanc service is already running; refusing to overwrite it.' >&2
  exit 1
fi
if ss -ltnH 'sport = :8043' | grep -q .; then
  echo 'Port 8043 is occupied; refusing to replace the listener.' >&2
  exit 1
fi
if test -e storage/orthanc/config.json; then
  echo 'Existing configuration found; resume manually without regenerating credentials.' >&2
  exit 1
fi

.venv/bin/python tools/orthanc_demo.py prepare
curl --fail --location --retry 2 --connect-timeout 20 --max-time 600 \
  https://orthanc.uclouvain.be/downloads/linux-standard-base/orthanc/1.13.0/Orthanc \
  --output storage/orthanc/bin/Orthanc.download
chmod 700 storage/orthanc/bin/Orthanc.download
storage/orthanc/bin/Orthanc.download --version
mv storage/orthanc/bin/Orthanc.download storage/orthanc/bin/Orthanc
sudo install -m 644 deploy/orthanc/aiwork-orthanc.service /etc/systemd/system/aiwork-orthanc.service
sudo systemctl daemon-reload
sudo systemctl start aiwork-orthanc.service
trap 'sudo systemctl stop aiwork-orthanc.service; echo "Stopped incomplete Orthanc deployment; keep backups and inspect configuration." >&2' ERR
for attempt in $(seq 1 20); do
  if ss -ltnH 'sport = :8043' | grep -q '127.0.0.1:8043'; then break; fi
  sleep 1
done
listeners=$(ss -ltnH 'sport = :8043')
test "$(printf '%s\n' "$listeners" | wc -l)" -eq 1
printf '%s\n' "$listeners" | grep -q '127.0.0.1:8043'
.venv/bin/python tools/orthanc_demo.py seed
# Restart the portal only after confirming there are no active background jobs.
.venv/bin/python -c 'from app.db import connect; c=connect(); n=c.execute("SELECT COUNT(*) FROM processing_jobs WHERE status IN (\"queued\",\"running\")").fetchone()[0]; c.close(); assert n == 0, "Active jobs: postpone portal restart"'
sudo systemctl restart ai-work.service
for attempt in $(seq 1 30); do
  if curl --fail --silent http://127.0.0.1:8000/healthz >/dev/null; then break; fi
  sleep 1
done
curl --fail --silent http://127.0.0.1:8000/healthz
.venv/bin/python tools/orthanc_demo.py activate
sudo systemctl enable aiwork-orthanc.service
trap - ERR
echo 'Orthanc is bound only to 127.0.0.1:8043. Portal verification is still required.'
