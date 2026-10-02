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
- `INSTAGRAM_REDIRECT_URI` (aliases: `META_INSTAGRAM_REDIRECT_URI`, `META_CALLBACK_URL`) — callback de Next (`/auth/instagram/callback`); debe coincidir con Meta
- `INSTAGRAM_TOKEN_ENCRYPTION_KEY` — 64 caracteres hex (32 bytes) para AES-GCM
- `TURSO_URL` (alias: `TURSO_DATABASE_URL`) — `libsql://...` o `file:./instagram.db`
- `TURSO_TOKEN` (alias: `TURSO_AUTH_TOKEN`)
- `INSTAGRAM_SNAPSHOT_JOB_TOKEN` — opcional; protege `POST /internal/instagram/snapshots`

`INSTAGRAM_APP_SECRET` y los access tokens nunca salen al frontend.

En el dashboard de Meta, registrá exactamente el mismo redirect URI.

Callbacks que Meta llama (expuestos solo esas rutas vía nginx → backend):

- Deauthorize callback: `https://<dominio>/instagram/deauthorize`
- Data deletion request: `https://<dominio>/instagram/data-deletion`

## Desarrollo local

Turso Cloud se usa si `TURSO_URL` es `libsql://` o `https://`. Sin cuenta de Turso:

```env
TURSO_URL=file:./instagram.db
TURSO_TOKEN=
```

### OAuth redirect en localhost

El callback vive en Next (`/auth/instagram/callback`). En Meta registrá exactamente el mismo URI que `INSTAGRAM_REDIRECT_URI` (Meta suele exigir `https://`).

## API

- `GET /me/instagram/connect` — URL de Instagram Login (JWT)
- `POST /me/instagram/oauth` — completa el OAuth (JWT); lo llama el route handler de Next
- `GET /me/instagram` — estado de la conexión y último snapshot (sin token)
- `GET /me/instagram/followers` — historial semanal
- `DELETE /me/instagram`
- `POST /instagram/deauthorize` — callback de Meta (signed_request)
- `POST /instagram/data-deletion` — callback de Meta; responde `{url, confirmation_code}`
- `GET /instagram/data-deletion/status` — estado de la solicitud de borrado
- `POST /internal/instagram/snapshots` — job (`X-Job-Token`); en producción preferí `docker compose exec` diario ([VPS_DEPLOY_REVIEW §7.5](./VPS_DEPLOY_REVIEW.md#75-job-de-snapshots))

Permiso de Meta: `instagram_business_basic` (incluye `followers_count`).

## Snapshots (captura diaria, valor semanal)

Una captura por cuenta y por semana ISO (lunes 00:00 UTC). Si el job corre dos veces la misma semana, se actualiza la misma fila. En producción conviene un cron **diario** para renovar tokens (ventana de 7 días antes del vencimiento de 60).

```bash
cd backend
uv run python run_instagram_snapshots.py
# exit 1 si failed > 0
```

En el VPS: `./deploy/run-snapshots.sh` (cron diario; ver `VPS_DEPLOY_REVIEW.md` §7.5). El endpoint HTTP con `INSTAGRAM_SNAPSHOT_JOB_TOKEN` es opcional.

## Tests

No necesitan Supabase:

```bash
cd backend
uv run pytest tests/unit/instagram tests/integration/instagram
```

Los tests de persistencia usan SQLite en memoria. El cliente HTTP de Turso y el de Meta están cubiertos con `httpx.MockTransport`.
