#!/usr/bin/env sh
# Renovación de certificados + reload de nginx. Cron sugerido:
#   15 3 * * * cd /opt/sellonomada && ./deploy/renew-certs.sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
COMPOSE="docker compose -f ${ROOT}/docker-compose.prod.yml --profile certs"

${COMPOSE} run --rm --entrypoint certbot certbot renew --webroot -w /var/www/certbot
${COMPOSE} exec -T nginx nginx -s reload
