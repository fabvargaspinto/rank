from fastapi import FastAPI

from controller.auth_route import router as auth_router
from controller.error_handlers import register_error_handlers

app = FastAPI()
register_error_handlers(app)
app.include_router(auth_router)
