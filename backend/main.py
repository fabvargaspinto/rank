from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.body_limit import register_body_limit
from api.dependencies.container import get_dependency_container
from api.errors import register_error_handlers
from api.logging import configure_logging
from api.rate_limit import register_rate_limit
from api.request_id import register_request_id
from api.routers.health import router as health_router
from api.routers.instagram import router as instagram_router
from api.routers.me import router as me_router
from api.routers.profiles import router as profiles_router
from api.routers.session import router as session_router
from config.app_settings import AppSettings
from config.instagram_settings import InstagramSettings
from config.turso_settings import TursoSettings


@asynccontextmanager
async def _lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    app_settings = AppSettings()
    if app_settings.is_production:
        TursoSettings().require_remote_for_production()
    get_dependency_container()
    InstagramSettings()  # type: ignore[call-arg]
    yield


def create_app() -> FastAPI:
    settings = AppSettings()
    docs_url = None if settings.is_production else "/docs"
    redoc_url = None if settings.is_production else "/redoc"
    openapi_url = None if settings.is_production else "/openapi.json"
    app = FastAPI(
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
        lifespan=_lifespan,
    )
    register_body_limit(app)
    register_request_id(app)
    register_error_handlers(app)
    register_rate_limit(app)
    app.include_router(health_router)
    app.include_router(session_router)
    app.include_router(me_router)
    app.include_router(instagram_router)
    app.include_router(profiles_router)
    return app


app = create_app()
