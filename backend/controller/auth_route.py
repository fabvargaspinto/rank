from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies.auth import CurrentUser, get_current_user
from api.schemas.auth import SessionResponse
from config.dependency_container import get_ensure_user_provisioned
from core.auth.application.ensure_user_provisioned import EnsureUserProvisioned

router = APIRouter()


@router.post("/auth/session", response_model=SessionResponse)
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
