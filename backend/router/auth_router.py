from fastapi import APIRouter

from pydantic import BaseModel

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
    return {"message": "User registered successfully"}