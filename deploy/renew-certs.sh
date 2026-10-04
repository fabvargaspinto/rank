#!/usr/bin/env sh
# Renovación de certificados + reload de nginx.
# Cron sugerido (con pipefail para que exit ≠ 0 llegue a cron/journald):
#   15 3 * * * bash -lc 'set -o pipefail; cd /opt/sellonomada && ./deploy/renew-certs.sh 2>&1 | logger -t sellonomada-certs'
# Complemento: monitor externo del vencimiento TLS (Uptime Kuma / Better Stack).
# Logs: journalctl -t sellonomada-certs
set -eu

ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
COMPOSE="docker compose -f ${ROOT}/docker-compose.prod.yml --profile certs"

${COMPOSE} run --rm --entrypoint certbot certbot renew --webroot -w /var/www/certbot
${COMPOSE} exec -T nginx nginx -s reload
