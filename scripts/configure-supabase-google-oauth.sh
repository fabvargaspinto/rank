#!/usr/bin/env bash
# Configura el proveedor Google en Auth del proyecto Supabase hosted (sección 6.3).
# El Client ID/Secret NO van en el .env de la app: solo en Supabase (o este script).
#
# Uso:
#   export SUPABASE_ACCESS_TOKEN=sbp_…
#   export GOOGLE_CLIENT_ID=….apps.googleusercontent.com
#   export GOOGLE_CLIENT_SECRET=…
#   ./scripts/configure-supabase-google-oauth.sh
#
# En Google Cloud → Credenciales OAuth:
#   Authorized redirect URI = https://<PROJECT_REF>.supabase.co/auth/v1/callback
# En Google Cloud → Pantalla de consentimiento: publicar (In production) + dominio,
# logo y enlaces a /privacidad y /terminos.

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

CLIENT_ID="${GOOGLE_CLIENT_ID:-}"
CLIENT_SECRET="${GOOGLE_CLIENT_SECRET:-}"
if [[ -z "$CLIENT_ID" || -z "$CLIENT_SECRET" ]]; then
  echo "Faltan GOOGLE_CLIENT_ID y GOOGLE_CLIENT_SECRET (solo para este script; no los usa la app)." >&2
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
  echo "No pude deducir PROJECT_REF. Pasalo: PROJECT_REF=xxxx $0" >&2
  exit 1
fi

echo "Proyecto: $REF"
echo "Google client: ${CLIENT_ID:0:12}…"
echo "Redirect URI en Google Cloud (obligatoria):"
echo "  https://${REF}.supabase.co/auth/v1/callback"

PAYLOAD=$(
  CLIENT_ID="$CLIENT_ID" \
  CLIENT_SECRET="$CLIENT_SECRET" \
  python3 - <<'PY'
import json, os
print(json.dumps({
    "external_google_enabled": True,
    "external_google_client_id": os.environ["CLIENT_ID"],
    "external_google_secret": os.environ["CLIENT_SECRET"],
}))
PY
)

HTTP_CODE=$(curl -sS -o /tmp/supabase-google-oauth-response.json -w "%{http_code}" \
  -X PATCH "https://api.supabase.com/v1/projects/${REF}/config/auth" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

if [[ "$HTTP_CODE" != "200" ]]; then
  echo "Error HTTP $HTTP_CODE:" >&2
  cat /tmp/supabase-google-oauth-response.json >&2
  echo >&2
  exit 1
fi

echo "OK: Google OAuth habilitado en Auth de $REF."
echo "Pendiente en Google Cloud (no lo cubre este script):"
echo "  - Pantalla de consentimiento publicada (In production)"
echo "  - Dominio verificado + logo + /privacidad y /terminos"
echo "  - Authorized redirect URI = https://${REF}.supabase.co/auth/v1/callback"
