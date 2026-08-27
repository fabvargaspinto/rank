from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from core.auth.application.register_auth import RegisterAuth
from dependencies import AuthRepoDep

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)




class RegisterRequest(BaseModel):
    email: str
    password: str
    provider: str
    name: str


@auth_router.post("/register")
async def register(request: RegisterRequest, auth_repo: AuthRepoDep):
    register_auth = RegisterAuth(auth_repo=auth_repo)
    register_auth.register(request.email, request.password, request.provider, request.name)
    return JSONResponse(status_code=200, content={"message": "User registered successfully"})