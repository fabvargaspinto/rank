#!/usr/bin/env bash
# Configura SMTP Resend + límite de emails en un proyecto Supabase hosted.
#
# Antes de correrlo:
#   1. Verificá un dominio (o subdominio de envío, p. ej. mail.tudominio.com) en Resend:
#      SPF + DKIM. Publicá DMARC con p=none al principio.
#   2. Creá una API key de producción con “Sending access” limitado a ese dominio.
#      No reutilices la RESEND_API_KEY del .env local (supabase/config.toml).
#   3. Definí RESEND_FROM_EMAIL con una casilla de ese dominio (nunca beth.t@example.com).
#
# Uso:
#   export SUPABASE_ACCESS_TOKEN=sbp_…   # https://supabase.com/dashboard/account/tokens
#   export RESEND_API_KEY=re_…          # key de producción, no la de local
#   export RESEND_FROM_EMAIL=noreply@mail.tudominio.com
#   ./scripts/configure-resend-smtp.sh
# Opcional: PROJECT_REF=xxxx  RESEND_SENDER_NAME=…  RATE_LIMIT_EMAIL_SENT=30

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Token y API key de prod: solo export explícito (no la RESEND_* del .env local).
TOKEN="${SUPABASE_ACCESS_TOKEN:-}"
API_KEY="${RESEND_API_KEY:-${RESENDER_API_KEY:-}}"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

if [[ -z "$TOKEN" ]]; then
  echo "Falta SUPABASE_ACCESS_TOKEN exportado (https://supabase.com/dashboard/account/tokens)." >&2
  echo "No lo guardes en .env: controla todos tus proyectos." >&2
  exit 1
fi

if [[ -z "$API_KEY" ]]; then
  echo "Exportá RESEND_API_KEY de producción (no uses la del .env local)." >&2
  exit 1
fi

FROM_EMAIL="${RESEND_FROM_EMAIL:-}"
if [[ -z "$FROM_EMAIL" ]]; then
  echo "Falta RESEND_FROM_EMAIL (casilla de tu dominio verificado en Resend)." >&2
  echo "Ejemplo: RESEND_FROM_EMAIL=noreply@mail.tudominio.com" >&2
  exit 1
fi

if [[ "$FROM_EMAIL" == "beth.t@example.com" ]]; then
  echo "RESEND_FROM_EMAIL no puede ser beth.t@example.com en producción." >&2
  echo "Verificá un dominio en Resend (SPF/DKIM) y usá una casilla de ese dominio." >&2
  exit 1
fi

if [[ ! "$FROM_EMAIL" =~ ^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$ ]]; then
  echo "RESEND_FROM_EMAIL no parece un email válido: $FROM_EMAIL" >&2
  exit 1
fi

SENDER_NAME="${RESEND_SENDER_NAME:-Sellonomada}"
EMAIL_LIMIT="${RATE_LIMIT_EMAIL_SENT:-30}"

REF="${PROJECT_REF:-}"
if [[ -z "$REF" ]]; then
  URL="${SUPABASE_URL:-${NEXT_PUBLIC_SUPABASE_URL:-}}"
  if [[ "$URL" =~ https://([a-z0-9]+)\.supabase\.co ]]; then
    REF="${BASH_REMATCH[1]}"
  fi
fi
if [[ -z "$REF" ]]; then
  echo "No pude deducir PROJECT_REF. Pasalo explícito: PROJECT_REF=xxxx $0" >&2
  exit 1
fi

echo "Proyecto: $REF"
echo "Sender:   $FROM_EMAIL ($SENDER_NAME)"
echo "Límite:   $EMAIL_LIMIT emails/hora"
echo "Aviso:    la API key tiene que ser de producción (Sending access al dominio verificado)."

PAYLOAD=$(
  FROM_EMAIL="$FROM_EMAIL" \
  SENDER_NAME="$SENDER_NAME" \
  API_KEY="$API_KEY" \
  EMAIL_LIMIT="$EMAIL_LIMIT" \
  python3 - <<'PY'
import json, os
print(json.dumps({
    "external_email_enabled": True,
    "mailer_autoconfirm": False,
    "smtp_admin_email": os.environ["FROM_EMAIL"],
    "smtp_host": "smtp.resend.com",
    "smtp_port": "465",
    "smtp_user": "resend",
    "smtp_pass": os.environ["API_KEY"],
    "smtp_sender_name": os.environ["SENDER_NAME"],
    "rate_limit_email_sent": int(os.environ["EMAIL_LIMIT"]),
}))
PY
)

HTTP_CODE=$(curl -sS -o /tmp/supabase-smtp-response.json -w "%{http_code}" \
  -X PATCH "https://api.supabase.com/v1/projects/${REF}/config/auth" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

if [[ "$HTTP_CODE" != "200" ]]; then
  echo "Error HTTP $HTTP_CODE:" >&2
  cat /tmp/supabase-smtp-response.json >&2
  echo >&2
  exit 1
fi

echo "OK: SMTP Resend aplicado en $REF (límite $EMAIL_LIMIT/h)."
echo "Confirmá en Resend que el dominio de $FROM_EMAIL está verificado (SPF/DKIM) y DMARC en p=none."
