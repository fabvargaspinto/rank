from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr

from config.dependency_container import DependencyContainer, get_dependency_container
from core.auth.application.register_user import RegisterUserUseCase
from core.auth.domain.auth_oauth_provider import AuthOauthProvider
from core.shared.domain.domain_error import DomainError

router = APIRouter(prefix="/auth", tags=["auth"])


def get_register_user_use_case(
    container: Annotated[DependencyContainer, Depends(get_dependency_container)],
) -> RegisterUserUseCase:
    return container.register_user_use_case()


class RegisterEmailRequest(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str


class RegisterOauthRequest(BaseModel):
    email: EmailStr
    oauth_provider: AuthOauthProvider
    oauth_provider_id: str


@router.post("/register/email")
def register_with_email(
    request: RegisterEmailRequest,
    use_case: Annotated[RegisterUserUseCase, Depends(get_register_user_use_case)],
) -> dict:
    try:
        use_case.with_email(
            request.email,
            request.password,
            request.confirm_password,
        )
    except DomainError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {"ok": True}


@router.post("/register/oauth")
def register_with_oauth(
    request: RegisterOauthRequest,
    use_case: Annotated[RegisterUserUseCase, Depends(get_register_user_use_case)],
) -> dict:
    try:
        use_case.with_oauth_provider(
            request.email,
            request.oauth_provider,
            request.oauth_provider_id,
        )
    except DomainError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {"ok": True}
