FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS base

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1


# ─────────────────────────────────────────────
# Dependencies
# ─────────────────────────────────────────────

FROM base AS deps

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project --no-dev


# ─────────────────────────────────────────────
# Development
# ─────────────────────────────────────────────

FROM deps AS dev

COPY . .

RUN uv sync --frozen --no-dev

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"

# Named volume /opt/venv can outlive the image; sync so new lockfile deps land.
CMD ["sh", "-c", "uv sync --frozen --no-dev && exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload"]


# ─────────────────────────────────────────────
# Production
# ─────────────────────────────────────────────

FROM deps AS prod

COPY . .

RUN uv sync --frozen --no-dev

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]