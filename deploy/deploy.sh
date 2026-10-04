#!/usr/bin/env sh
# Deploy con verificación y rollback.
# Uso (en el VPS, desde /opt/sellonomada o la raíz del repo):
#   ./deploy/deploy.sh <tag>   # SHA del push, o <sha>-YYYYMMDD del schedule semanal
#
# Requiere .env junto a docker-compose.prod.yml con TAG= y DOMAIN=.
set -eu

ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
cd "${ROOT}"

NEW_TAG="${1:?pasá el tag a desplegar (SHA de un push, o SHA-YYYYMMDD del rebuild semanal)}"
ENV_FILE="${ROOT}/.env"
COMPOSE="docker compose -f docker-compose.prod.yml"

if [ ! -f "${ENV_FILE}" ]; then
  echo "Falta ${ENV_FILE} (copiá deploy/compose.env.example)." >&2
  exit 1
fi

OLD_TAG="$(sed -n 's/^TAG=//p' "${ENV_FILE}" | head -n 1)"
DOMAIN="$(sed -n 's/^DOMAIN=//p' "${ENV_FILE}" | head -n 1)"

if [ -z "${DOMAIN}" ]; then
  echo "Falta DOMAIN= en ${ENV_FILE}." >&2
  exit 1
fi

if [ -z "${OLD_TAG}" ]; then
  echo "Falta TAG= actual en ${ENV_FILE} (necesario para poder volver atrás)." >&2
  exit 1
fi

if [ "${NEW_TAG}" = "${OLD_TAG}" ]; then
  echo "TAG ya es ${NEW_TAG}; nada que hacer."
  exit 0
fi

set_tag() {
  if grep -q '^TAG=' "${ENV_FILE}"; then
    sed -i "s/^TAG=.*/TAG=$1/" "${ENV_FILE}"
  else
    echo "TAG=$1" >>"${ENV_FILE}"
  fi
}

rollback() {
  echo "Falló ${NEW_TAG}; vuelvo a ${OLD_TAG}" >&2
  set_tag "${OLD_TAG}"
  if ! ${COMPOSE} up -d --wait --wait-timeout 120; then
    echo "También falló el rollback a ${OLD_TAG}. Revisá a mano." >&2
  fi
}

echo "Deploy ${OLD_TAG} → ${NEW_TAG} (https://${DOMAIN})"
set_tag "${NEW_TAG}"

if ! ${COMPOSE} pull; then
  rollback
  exit 1
fi

if ! ${COMPOSE} up -d --wait --wait-timeout 120; then
  rollback
  exit 1
fi

if ! curl -fsS --max-time 15 "https://${DOMAIN}/robots.txt" >/dev/null; then
  echo "Smoke test falló: https://${DOMAIN}/robots.txt" >&2
  rollback
  exit 1
fi

docker image prune -af --filter "until=168h" >/dev/null
echo "OK: ${NEW_TAG}"
