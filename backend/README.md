# Backend (FastAPI)

API del monolito: Linktree (`core.auth`, `core.user`, `core.post`) + Instagram Analytics (`core.instagram`).

## Setup

```bash
cd backend
uv sync
cp ../.env.example ../.env   # completar variables
uv run uvicorn main:app --reload --port 8000
```

## Variables

Ver `.env.example` en la raíz del repo y [`docs/INSTAGRAM_ANALYTICS.md`](../docs/INSTAGRAM_ANALYTICS.md). En producción el contenedor usa `deploy/backend.env` ([`docs/VPS_DEPLOY_REVIEW.md`](../docs/VPS_DEPLOY_REVIEW.md) §7.8).

## Tests

```bash
uv run pytest tests/unit -q
uv run pytest tests/integration -q   # requiere Supabase local o SUPABASE_DEVELOPMENT_*
```

## Despliegue

Imagen Docker `target: production`, compose de prod y checklist en [`docs/VPS_DEPLOY_REVIEW.md`](../docs/VPS_DEPLOY_REVIEW.md).
