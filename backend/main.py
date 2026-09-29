from contextlib import asynccontextmanager

from fastapi import FastAPI

from config.app_settings import AppSettings
from controller.auth_route import router as auth_router
from controller.body_limit import register_body_limit
from controller.comment_route import router as comment_router
from controller.error_handlers import register_error_handlers
from controller.health_route import router as health_router
from controller.logging_config import configure_logging
from controller.rate_limit import register_rate_limit
from controller.request_id import register_request_id
from controller.user_route import router as user_router


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    configure_logging()
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
    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(comment_router)
    return app


app = create_app()
