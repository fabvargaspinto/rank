#!/bin/sh
# Genera un certificado autofirmado temporal si aún no hay uno de Let's Encrypt,
# para que nginx pueda arrancar en 443 la primera vez.
set -eu

DOMAIN="${DOMAIN:?DOMAIN is required}"
LIVE_DIR="/etc/letsencrypt/live/${DOMAIN}"

if [ -f "${LIVE_DIR}/fullchain.pem" ] && [ -f "${LIVE_DIR}/privkey.pem" ]; then
    exit 0
fi

echo "No hay certificado de Let's Encrypt para ${DOMAIN}; generando autofirmado temporal"
mkdir -p "${LIVE_DIR}"
apk add --no-cache openssl >/dev/null
openssl req -x509 -nodes -newkey rsa:2048 -days 2 \
    -keyout "${LIVE_DIR}/privkey.pem" \
    -out "${LIVE_DIR}/fullchain.pem" \
    -subj "/CN=${DOMAIN}"
