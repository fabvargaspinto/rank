#!/usr/bin/env sh
# Primer certificado Let's Encrypt (webroot). Ejecutar en el VPS con DNS
# apuntando al servidor y el stack ya arriba (nginx sirviendo el challenge):
#
#   DOMAIN=ejemplo.com EMAIL=ops@ejemplo.com ./deploy/obtain-cert.sh
#
set -eu

ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
COMPOSE="docker compose -f ${ROOT}/docker-compose.prod.yml --profile certs"
DOMAIN="${DOMAIN:?definí DOMAIN}"
EMAIL="${EMAIL:?definí EMAIL}"

# Quitar autofirmado temporal del entrypoint para que certbot pueda emitir.
${COMPOSE} run --rm --entrypoint sh certbot -c \
    "rm -rf /etc/letsencrypt/live/${DOMAIN} \
            /etc/letsencrypt/archive/${DOMAIN} \
            /etc/letsencrypt/renewal/${DOMAIN}.conf"

${COMPOSE} run --rm --entrypoint certbot certbot certonly \
    --webroot -w /var/www/certbot \
    --email "${EMAIL}" \
    --agree-tos \
    --no-eff-email \
    -d "${DOMAIN}" \
    -d "www.${DOMAIN}"

${COMPOSE} exec -T nginx nginx -s reload
echo "Certificado instalado y nginx recargado para ${DOMAIN}"
