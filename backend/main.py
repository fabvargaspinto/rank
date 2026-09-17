from fastapi import FastAPI

from controller.auth_route import router as auth_router
from controller.error_handlers import register_error_handlers
from controller.health_route import router as health_router
from controller.request_id import register_request_id
from controller.user_route import router as user_router

app = FastAPI()
register_request_id(app)
register_error_handlers(app)
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(user_router)
