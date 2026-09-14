from typing import Annotated

from fastapi import APIRouter, Depends, Header

from api.dependencies.auth import (
    CurrentUser,
    extract_bearer_token,
    get_current_user,
)
from config.dependency_container import get_ensure_user_provisioned
from core.auth.application.ensure_user_provisioned import EnsureUserProvisioned

router = APIRouter()


@router.post("/auth/session")
def provision_session(
    _current_user: Annotated[CurrentUser, Depends(get_current_user)],
    authorization: Annotated[str | None, Header()] = None,
    ensure_user_provisioned: EnsureUserProvisioned = Depends(
        get_ensure_user_provisioned
    ),
):
    auth = ensure_user_provisioned.execute(extract_bearer_token(authorization))

    return {
        "id": auth.id.value,
    }
