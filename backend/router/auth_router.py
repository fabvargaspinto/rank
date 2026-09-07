from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from core.auth.application.login_auth import LoginAuth
from core.auth.domain.auth import Auth
from core.auth.domain.auth_repo import AuthSession, RegisterAuthResult
from dependencies import AuthRepoDep, RegisterAuthDep

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


class RegisterCredentialsRequest(BaseModel):
    email: str
    name: str
    password: str
    confirm_password: str


class RegisterGoogleRequest(BaseModel):
    email: str
    name: str
    provider_id: str


class LoginRequest(BaseModel):
    email: str
    password: str


def _serialize_auth(auth: Auth) -> dict:
    return {
        "id": auth.id.value,
        "user_id": auth.user_id.value,
        "email": auth.email.value,
        "provider": str(auth.provider),
        "created_at": auth.created_at.value.isoformat(),
        "last_login_at": (
            auth.last_login_at.value.isoformat() if auth.last_login_at else None
        ),
        "provider_id": auth.provider_id,
    }


def _serialize_session(session: AuthSession) -> dict:
    return {
        "access_token": session.access_token,
        "refresh_token": session.refresh_token,
        "expires_in": session.expires_in,
    }


def _register_response(result: RegisterAuthResult) -> JSONResponse:
    return JSONResponse(
        content={
            "message": "usuario registrado correctamente",
            "isError": False,
            "data": {
                **_serialize_auth(result.auth),
                "session": (
                    _serialize_session(result.session) if result.session else None
                ),
            },
        },
        status_code=201,
    )


@auth_router.post("/register/credentials")
def register_credentials(
    request: RegisterCredentialsRequest,
    register_auth: RegisterAuthDep,
) -> JSONResponse:
    try:
        result = register_auth.register_with_credentials(
            email=request.email,
            name=request.name,
            password=request.password,
            confirm_password=request.confirm_password,
        )
        return _register_response(result)
    except Exception as error:
        return JSONResponse(
            content={"message": str(error), "isError": True},
            status_code=400,
        )


@auth_router.post("/register/google")
def register_google(
    request: RegisterGoogleRequest,
    register_auth: RegisterAuthDep,
) -> JSONResponse:
    try:
        result = register_auth.register_with_google(
            email=request.email,
            name=request.name,
            provider_id=request.provider_id,
        )
        return _register_response(result)
    except Exception as error:
        return JSONResponse(
            content={"message": str(error), "isError": True},
            status_code=400,
        )


@auth_router.post("/login")
def login(request: LoginRequest, auth_repo: AuthRepoDep) -> JSONResponse:
    try:
        session = LoginAuth(auth_repo=auth_repo).login(
            email=request.email,
            password=request.password,
        )
        return JSONResponse(
            content={
                "message": "sesión iniciada correctamente",
                "isError": False,
                "data": _serialize_session(session),
            },
            status_code=200,
        )
    except Exception as error:
        return JSONResponse(
            content={"message": str(error), "isError": True},
            status_code=401,
        )
