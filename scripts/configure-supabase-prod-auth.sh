#!/usr/bin/env bash
# Configura Auth del proyecto Supabase hosted para producción (sección 6.1).
# No crea el proyecto ni aplica migraciones: eso es aparte (supabase link / db push).
#
# Uso:
#   export SUPABASE_ACCESS_TOKEN=sbp_…   # https://supabase.com/dashboard/account/tokens
#   export SITE_URL=https://tu-dominio   # o NEXT_PUBLIC_SITE_URL
#   ./scripts/configure-supabase-prod-auth.sh
#
# Opcional:
#   PROJECT_REF=xxxx
#   SKIP_TEMPLATES=1   # no subir HTML de supabase/templates/

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

SITE_URL="${SITE_URL:-${NEXT_PUBLIC_SITE_URL:-}}"
SITE_URL="${SITE_URL%/}"
if [[ -z "$SITE_URL" || "$SITE_URL" == http://localhost* || "$SITE_URL" == http://127.0.0.1* ]]; then
  echo "Falta SITE_URL de producción (https://…). No uses localhost." >&2
  exit 1
fi
if [[ "$SITE_URL" != https://* ]]; then
  echo "SITE_URL debe ser https://… (ahora: $SITE_URL)" >&2
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

# lower_upper_letters_digits → clases separadas por ':'
PASSWORD_CHARS='abcdefghijklmnopqrstuvwxyz:ABCDEFGHIJKLMNOPQRSTUVWXYZ:0123456789'

REDIRECTS=(
  "${SITE_URL}/auth/callback"
  "${SITE_URL}/auth/confirm"
  "${SITE_URL}/auth/confirm?next=/reset-password"
  "${SITE_URL}/reset-password"
)

echo "Proyecto:  $REF"
echo "Site URL:  $SITE_URL"
echo "Redirects: ${REDIRECTS[*]}"

SITE_URL="$SITE_URL" \
REDIRECTS="$(printf '%s\n' "${REDIRECTS[@]}")" \
PASSWORD_CHARS="$PASSWORD_CHARS" \
ROOT="$ROOT" \
SKIP_TEMPLATES="${SKIP_TEMPLATES:-0}" \
python3 - <<'PY' > /tmp/supabase-prod-auth-payload.json
import json, os
from pathlib import Path

site = os.environ["SITE_URL"]
redirects = [u for u in os.environ["REDIRECTS"].split("\n") if u.strip()]
chars = os.environ["PASSWORD_CHARS"]
root = Path(os.environ["ROOT"])

payload = {
    "site_url": site,
    "uri_allow_list": ",".join(redirects),
    "mailer_autoconfirm": False,
    "password_min_length": 8,
    "password_required_characters": chars,
    "security_update_password_require_reauthentication": True,
}

if os.environ.get("SKIP_TEMPLATES") != "1":
    confirmation = root / "supabase/templates/confirmation.html"
    recovery = root / "supabase/templates/recovery.html"
    if confirmation.is_file():
        payload["mailer_subjects_confirmation"] = "Confirmá tu cuenta"
        payload["mailer_templates_confirmation_content"] = confirmation.read_text(
            encoding="utf-8"
        )
    if recovery.is_file():
        payload["mailer_subjects_recovery"] = "Recuperá tu contraseña"
        payload["mailer_templates_recovery_content"] = recovery.read_text(
            encoding="utf-8"
        )

print(json.dumps(payload))
PY

HTTP_CODE=$(curl -sS -o /tmp/supabase-prod-auth-response.json -w "%{http_code}" \
  -X PATCH "https://api.supabase.com/v1/projects/${REF}/config/auth" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d @/tmp/supabase-prod-auth-payload.json)

if [[ "$HTTP_CODE" != "200" ]]; then
  echo "Error HTTP $HTTP_CODE:" >&2
  cat /tmp/supabase-prod-auth-response.json >&2
  echo >&2
  exit 1
fi

echo "OK: Auth de producción aplicado en $REF."
echo "Pendiente en el dashboard (no lo cubre este script):"
echo "  - Proyecto nuevo + migraciones (supabase db push)"
echo "  - Plan / backups"
echo "  - SMTP Resend: ./scripts/configure-resend-smtp.sh"
echo "  - CAPTCHA + IP Address Forwarding"
echo "  - Claves JWT asimétricas (ES256/RS256)"
echo "  - Google OAuth de producción"
echo "  - Security / Performance Advisor"
