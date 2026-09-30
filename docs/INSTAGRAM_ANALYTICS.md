# Instagram Analytics

Bounded context independiente del Linktree. Vive en el monolito FastAPI (`backend/core/instagram`) con persistencia propia (Turso o SQLite). El contexto Linktree no importa este código.

## Separación

| Contexto | Persistencia | Identidad |
| --- | --- | --- |
| Linktree (`core.auth`, `core.user`, `core.post`) | Supabase/PostgreSQL | `User` |
| Instagram Analytics (`core.instagram`) | Turso/SQLite | `owner_user_id` (UUID externo) |

No hay foreign keys entre las dos bases. El adapter HTTP (`api/routers/instagram.py`) toma `profile.id` del usuario autenticado y lo pasa como `owner_user_id`.

## Variables de entorno

Ver `.env.example`. Canónicas:

- `INSTAGRAM_APP_ID` (aliases: `META_APP_ID`, `META_ID_APP`) — Instagram App ID, no el App ID de Facebook
- `INSTAGRAM_APP_SECRET` (alias: `META_APP_SECRET`)
- `INSTAGRAM_REDIRECT_URI` (aliases: `META_INSTAGRAM_REDIRECT_URI`, `META_CALLBACK_URL`) — callback del backend; debe coincidir con Meta. En local Meta suele exigir `https://localhost:8000/instagram/oauth/callback`
- `INSTAGRAM_TOKEN_ENCRYPTION_KEY` — 64 caracteres hex (32 bytes) para AES-GCM
- `FRONTEND_URL` (alias: `NEXT_PUBLIC_SITE_URL`)
- `TURSO_URL` (alias: `TURSO_DATABASE_URL`) — `libsql://...` o `file:./instagram.db`
- `TURSO_TOKEN` (alias: `TURSO_AUTH_TOKEN`)
- `INSTAGRAM_SNAPSHOT_JOB_TOKEN` — opcional; protege `POST /internal/instagram/snapshots`

`INSTAGRAM_APP_SECRET` y los access tokens nunca salen al frontend.

En el dashboard de Meta, registrá exactamente el mismo redirect URI.

## Desarrollo local

Turso Cloud se usa si `TURSO_URL` es `libsql://` o `https://`. Sin cuenta de Turso:

```env
TURSO_URL=file:./instagram.db
TURSO_TOKEN=
```

### OAuth redirect HTTPS en localhost

Meta exige un redirect `https://...`. Para desarrollo local usamos TLS con **mkcert** (certificado de confianza en tu Mac):

```bash
brew install mkcert nss
mkcert -install   # pide tu password una vez; confía la CA local
mkdir -p backend/certs
mkcert -cert-file backend/certs/localhost-cert.pem \
  -key-file backend/certs/localhost-key.pem \
  localhost 127.0.0.1 ::1
docker compose up -d --force-recreate backend
```

En Meta y en `.env`:

```env
INSTAGRAM_REDIRECT_URI=https://localhost:8000/instagram/oauth/callback
```

Si ves `Your connection is not private` / `ERR_CERT_AUTHORITY_INVALID`, falta `mkcert -install` (la CA local no está en el Keychain).

Sin certs en `backend/certs/`, el backend arranca en HTTP y el callback HTTPS de Meta no funciona.

## API

- `GET /me/instagram/connect` — URL de Instagram Login (JWT)
- `GET /instagram/oauth/callback` — callback de Meta; redirige a `/dashboard/tree?instagram=connected|error`
- `GET /me/instagram` — estado de la conexión y último snapshot (sin token)
- `GET /me/instagram/followers` — historial semanal
- `DELETE /me/instagram`
- `POST /internal/instagram/snapshots` — job semanal (`X-Job-Token`)

Permiso de Meta: `instagram_business_basic` (incluye `followers_count`).

## Snapshots semanales

Una captura por cuenta y por semana ISO (lunes 00:00 UTC). Si el job corre dos veces la misma semana, se actualiza la misma fila.

```bash
cd backend
uv run python run_instagram_snapshots.py
```

O un cron semanal contra `POST /internal/instagram/snapshots` con `INSTAGRAM_SNAPSHOT_JOB_TOKEN`.

## Tests

No necesitan Supabase:

```bash
cd backend
uv run pytest tests/unit/instagram tests/integration/instagram
```

Los tests de persistencia usan SQLite en memoria. El cliente HTTP de Turso y el de Meta están cubiertos con `httpx.MockTransport`.
