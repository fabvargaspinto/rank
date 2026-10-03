#!/usr/bin/env bash
# Activa hCaptcha en Supabase Auth (hosted).
# Uso:
#   export SUPABASE_ACCESS_TOKEN=sbp_…
#   export HCAPTCHA_SECRET_KEY=0x…
#   ./scripts/configure-supabase-hcaptcha.sh
# Opcional: PROJECT_REF=xxxx

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

if [[ -f deploy/frontend.env ]]; then
  set -a
  # shellcheck disable=SC1091
  source deploy/frontend.env
  set +a
fi

TOKEN="${SUPABASE_ACCESS_TOKEN:-}"
if [[ -z "$TOKEN" ]]; then
  echo "Falta SUPABASE_ACCESS_TOKEN (https://supabase.com/dashboard/account/tokens)" >&2
  exit 1
fi

SECRET="${HCAPTCHA_SECRET_KEY:-}"
if [[ -z "$SECRET" ]]; then
  echo "Falta HCAPTCHA_SECRET_KEY" >&2
  exit 1
fi

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
echo "CAPTCHA:  hcaptcha"

PAYLOAD=$(
  SECRET="$SECRET" \
  python3 - <<'PY'
import json, os
print(json.dumps({
    "security_captcha_enabled": True,
    "security_captcha_provider": "hcaptcha",
    "security_captcha_secret": os.environ["SECRET"],
}))
PY
)

HTTP_CODE=$(curl -sS -o /tmp/supabase-hcaptcha-response.json -w "%{http_code}" \
  -X PATCH "https://api.supabase.com/v1/projects/${REF}/config/auth" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

if [[ "$HTTP_CODE" != "200" ]]; then
  echo "Error HTTP $HTTP_CODE:" >&2
  cat /tmp/supabase-hcaptcha-response.json >&2
  echo >&2
  exit 1
fi

echo "OK: hCaptcha activado en Auth de $REF."
echo "Recordá:"
echo "  - NEXT_PUBLIC_HCAPTCHA_SITE_KEY en el build de la imagen del frontend"
echo "  - HCAPTCHA_SECRET_KEY en deploy/frontend.env (la app verifica el token; la secret key de Supabase Auth no lo hace)"
