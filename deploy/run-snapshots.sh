#!/usr/bin/env sh
# Job diario de captura de followers (misma imagen y env que el backend).
# Cron sugerido (con pipefail para que exit 1 llegue a cron/journald):
#   15 4 * * * bash -lc 'set -o pipefail; cd /opt/sellonomada && ./deploy/run-snapshots.sh 2>&1 | logger -t sellonomada-snapshots'
set -eu

ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
cd "${ROOT}"

docker compose -f docker-compose.prod.yml exec -T backend python run_instagram_snapshots.py
