from fastapi import APIRouter, Depends
from pydantic import BaseModel

from config.dependency_container import get_login_auth, get_register_auth
from core.auth.application.login_auth import LoginAuth
from core.auth.application.register_auth import RegisterAuth


class RegisterEmailRequest(BaseModel):
    email: str
    password: str
    confirm_password: str


class LoginEmailRequest(BaseModel):
    email: str
    password: str


class RegisterOAuthRequest(BaseModel):
    access_token: str


router = APIRouter()


@router.post("/auth/register/email")
def register_email(
    request: RegisterEmailRequest,
    register_auth: RegisterAuth = Depends(get_register_auth),
):
    auth = register_auth.with_email(
        email=request.email,
        password=request.password,
        confirm_password=request.confirm_password,
    )

    return {
        "id": auth.id.value,
    }


@router.post("/auth/login/email")
def login_email(
    request: LoginEmailRequest,
    login_auth: LoginAuth = Depends(get_login_auth),
):
    auth = login_auth.with_email(
        email=request.email,
        password=request.password,
    )

    return {
        "id": auth.id.value,
    }


@router.post("/auth/oauth")
def register_oauth(
    request: RegisterOAuthRequest,
    register_auth: RegisterAuth = Depends(get_register_auth),
):
    auth = register_auth.with_oauth_token(request.access_token)

    return {
        "id": auth.id.value,
    }
