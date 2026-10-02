#!/usr/bin/env bash
# Configura SMTP Resend + límite de emails en un proyecto Supabase hosted.
# Uso:
#   export SUPABASE_ACCESS_TOKEN=sbp_…   # https://supabase.com/dashboard/account/tokens
#   ./scripts/configure-resend-smtp.sh
# Opcional: PROJECT_REF=xxxx (si no, se deduce de SUPABASE_URL / NEXT_PUBLIC_SUPABASE_URL)

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

TOKEN="${SUPABASE_ACCESS_TOKEN:-}"
if [[ -z "$TOKEN" ]]; then
  echo "Falta SUPABASE_ACCESS_TOKEN (https://supabase.com/dashboard/account/tokens)" >&2
  exit 1
fi

API_KEY="${RESEND_API_KEY:-${RESENDER_API_KEY:-}}"
if [[ -z "$API_KEY" ]]; then
  echo "Falta RESEND_API_KEY (o RESENDER_API_KEY) en el entorno / .env" >&2
  exit 1
fi

FROM_EMAIL="${RESEND_FROM_EMAIL:-beth.t@example.com}"
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
RECIPIENT="${EMAIL_RECIPIENT:-${EMAIL_DEVELOPMENT_RECIPIENT:-}}"
if [[ -n "$RECIPIENT" ]]; then
  echo "Sin dominio verificado, Resend solo entrega a: $RECIPIENT"
fi
