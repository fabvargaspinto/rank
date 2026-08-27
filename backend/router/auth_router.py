from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from dependencies import RegisterAuthDep
from core.auth.domain.auth_error import (
    DuplicateAuthError,
    InvalidEmailError,
    InvalidPasswordError,
)
from core.share.infraestructure.infra_error import DatabaseError

auth_router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterBody(BaseModel):
    email: str
    password: str


@auth_router.post("/register")
def register(body: RegisterBody, register_auth: RegisterAuthDep):
    try:
        result = register_auth.execute(body.email, body.password)
    except (InvalidEmailError, InvalidPasswordError) as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    except DuplicateAuthError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))
    except DatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not register auth",
        )

    session = None
    if result.access_token and result.refresh_token:
        session = {
            "access_token": result.access_token,
            "refresh_token": result.refresh_token,
            "expires_in": result.expires_in,
        }

    return {
        "id": str(result.auth.id),
        "user_id": str(result.auth.user_id),
        "provider": str(result.auth.provider),
        "session": session,
    }


@auth_router.post("/login")
def login():
    return {"message": "Hello, World!"}


@auth_router.post("/logout")
def logout():
    return {"message": "Hello, World!"}
