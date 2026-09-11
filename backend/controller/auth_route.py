from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr

from config.dependency_container import DependencyContainer, get_dependency_container
from core.auth.application.login_user import LoginUserUseCase
from core.auth.application.register_user import RegisterUserUseCase
from core.auth.domain.auth_provider import AuthProvider
from core.shared.application.application_error import ApplicationError
from core.shared.domain.domain_error import DomainError

router = APIRouter(prefix="/auth", tags=["auth"])


def get_register_user_use_case(
    container: Annotated[DependencyContainer, Depends(get_dependency_container)],
) -> RegisterUserUseCase:
    return container.register_user_use_case()


def get_login_user_use_case(
    container: Annotated[DependencyContainer, Depends(get_dependency_container)],
) -> LoginUserUseCase:
    return container.login_user_use_case()


class RegisterEmailRequest(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str


class RegisterOauthRequest(BaseModel):
    email: EmailStr
    provider: AuthProvider
    provider_id: str


@router.post("/register/email")
def register_with_email(
    request: RegisterEmailRequest,
    use_case: Annotated[RegisterUserUseCase, Depends(get_register_user_use_case)],
) -> dict:
    return {"ok": True}


@router.post("/register/oauth")
def register_with_oauth(
    request: RegisterOauthRequest,
    use_case: Annotated[RegisterUserUseCase, Depends(get_register_user_use_case)],
) -> dict:
    return {"ok": True}


class LoginEmailRequest(BaseModel):
    email: EmailStr
    password: str


class LoginOauthRequest(BaseModel):
    email: EmailStr
    provider: AuthProvider
    provider_id: str


@router.post("/login/email")
def login_with_email(
    request: LoginEmailRequest,
    use_case: Annotated[LoginUserUseCase, Depends(get_login_user_use_case)],
) -> dict:
    return {"ok": True}


@router.post("/login/oauth")
def login_with_oauth(
    request: LoginOauthRequest,
    use_case: Annotated[LoginUserUseCase, Depends(get_login_user_use_case)],
) -> dict:
    return {"ok": True}
