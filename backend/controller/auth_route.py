from typing import Annotated

from fastapi import APIRouter, Depends, Header

from config.dependency_container import get_ensure_user_provisioned
from core.auth.application.application_error import InvalidAuthCredentialsError
from core.auth.application.ensure_user_provisioned import EnsureUserProvisioned

router = APIRouter()


def _bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise InvalidAuthCredentialsError(
            "El token de autenticación no es válido"
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise InvalidAuthCredentialsError(
            "El token de autenticación no es válido"
        )

    return token.strip()


@router.post("/auth/session")
def provision_session(
    authorization: Annotated[str | None, Header()] = None,
    ensure_user_provisioned: EnsureUserProvisioned = Depends(
        get_ensure_user_provisioned
    ),
):
    auth = ensure_user_provisioned.execute(_bearer_token(authorization))

    return {
        "id": auth.id.value,
    }
