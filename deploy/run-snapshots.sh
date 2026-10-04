#!/usr/bin/env sh
# Job diario de captura de followers (misma imagen y env que el backend).
# Cron sugerido (flock + pipefail + heartbeat solo si exit 0):
#   15 4 * * * bash -lc 'set -o pipefail; cd /opt/sellonomada && flock -n /tmp/sellonomada-snapshots.lock ./deploy/run-snapshots.sh 2>&1 | logger -t sellonomada-snapshots && curl -fsS -m 10 --retry 3 https://hc-ping.com/<uuid> >/dev/null'
set -eu

ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
cd "${ROOT}"

docker compose -f docker-compose.prod.yml exec -T backend python run_instagram_snapshots.py
