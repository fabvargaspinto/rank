from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.dependencies.auth import CurrentUser, get_current_user
from api.schemas.auth import ErrorResponse, SessionResponse
from config.dependency_container import get_ensure_user_provisioned
from core.auth.application.ensure_user_provisioned import EnsureUserProvisioned

router = APIRouter()


@router.post(
    "/auth/session",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Token ausente o inválido",
        },
        409: {
            "model": ErrorResponse,
            "description": "El email ya está registrado",
        },
    },
)
def provision_session(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    ensure_user_provisioned: EnsureUserProvisioned = Depends(
        get_ensure_user_provisioned
    ),
) -> SessionResponse:
    ensure_user_provisioned.execute(
        auth_id=current_user.auth_id,
        email=current_user.email,
    )
    return SessionResponse(provisioned=True)
