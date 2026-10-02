import hmac
from hashlib import sha256
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Header, HTTPException, Request, Response, status

from api.dependencies.container import (
    get_capture_instagram_followers_use_case,
    get_complete_instagram_oauth_use_case,
    get_delete_instagram_user_data_use_case,
    get_disconnect_instagram_use_case,
    get_follower_history_use_case,
    get_instagram_connection_use_case,
    get_start_instagram_connection_use_case,
)
from api.dependencies.current_profile import get_current_profile
from api.instagram_mapping import (
    to_follower_history_response,
    to_instagram_connection_response,
)
from api.rate_limit import limiter
from api.schemas.auth import ErrorResponse
from api.schemas.instagram import (
    CompleteInstagramOAuthRequest,
    FollowerHistoryResponse,
    InstagramConnectionResponse,
    InstagramConnectResponse,
    SnapshotJobResponse,
)
from config.instagram_settings import InstagramSettings
from core.instagram.application.capture_instagram_followers import (
    CaptureInstagramFollowers,
)
from core.instagram.application.complete_instagram_oauth import CompleteInstagramOAuth
from core.instagram.application.delete_instagram_user_data import (
    DeleteInstagramUserData,
    public_site_origin,
)
from core.instagram.application.disconnect_instagram import DisconnectInstagram
from core.instagram.application.get_follower_history import GetFollowerHistory
from core.instagram.application.get_instagram_connection import GetInstagramConnection
from core.instagram.application.start_instagram_connection import (
    StartInstagramConnection,
)
from core.instagram.infrastructure.signed_request import (
    InvalidSignedRequestError,
    parse_signed_request,
)
from core.user.domain.user import User

router = APIRouter()


def get_instagram_settings() -> InstagramSettings:
    return InstagramSettings()  # type: ignore[call-arg]


@router.get(
    "/me/instagram/connect",
    response_model=InstagramConnectResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "Token ausente o inválido"},
        404: {"model": ErrorResponse, "description": "Usuario no encontrado"},
        429: {"model": ErrorResponse, "description": "Demasiadas solicitudes"},
    },
)
@limiter.limit("10/minute")
def connect_instagram(
    request: Request,
    profile: Annotated[User, Depends(get_current_profile)],
    use_case: StartInstagramConnection = Depends(
        get_start_instagram_connection_use_case
    ),
) -> InstagramConnectResponse:
    return InstagramConnectResponse(
        authorization_url=use_case.execute(profile.id.value)
    )


@router.post(
    "/me/instagram/oauth",
    response_model=InstagramConnectionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "Token ausente o inválido"},
        400: {"model": ErrorResponse, "description": "OAuth inválido o denegado"},
        404: {"model": ErrorResponse, "description": "Usuario no encontrado"},
        409: {
            "model": ErrorResponse,
            "description": "Cuenta de Instagram ya vinculada",
        },
        429: {"model": ErrorResponse, "description": "Demasiadas solicitudes"},
    },
)
@limiter.limit("10/minute")
def complete_instagram_oauth(
    request: Request,
    body: CompleteInstagramOAuthRequest,
    profile: Annotated[User, Depends(get_current_profile)],
    use_case: CompleteInstagramOAuth = Depends(get_complete_instagram_oauth_use_case),
    connection_use_case: GetInstagramConnection = Depends(
        get_instagram_connection_use_case
    ),
) -> InstagramConnectionResponse:
    use_case.execute(
        profile.id.value,
        body.state or "",
        body.code,
        body.error,
    )
    return to_instagram_connection_response(
        connection_use_case.execute(profile.id.value)
    )


@router.get(
    "/me/instagram",
    response_model=InstagramConnectionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "Token ausente o inválido"},
        404: {"model": ErrorResponse, "description": "Usuario no encontrado"},
    },
)
def read_instagram(
    profile: Annotated[User, Depends(get_current_profile)],
    use_case: GetInstagramConnection = Depends(get_instagram_connection_use_case),
) -> InstagramConnectionResponse:
    return to_instagram_connection_response(use_case.execute(profile.id.value))


@router.delete(
    "/me/instagram",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Token ausente o inválido"},
        404: {"model": ErrorResponse, "description": "Usuario no encontrado"},
    },
)
def delete_instagram(
    profile: Annotated[User, Depends(get_current_profile)],
    use_case: DisconnectInstagram = Depends(get_disconnect_instagram_use_case),
) -> Response:
    use_case.execute(profile.id.value)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/me/instagram/followers",
    response_model=FollowerHistoryResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "Token ausente o inválido"},
        404: {"model": ErrorResponse, "description": "Usuario no encontrado"},
    },
)
def read_instagram_followers(
    profile: Annotated[User, Depends(get_current_profile)],
    use_case: GetFollowerHistory = Depends(get_follower_history_use_case),
) -> FollowerHistoryResponse:
    return to_follower_history_response(use_case.execute(profile.id.value))


@router.post(
    "/internal/instagram/snapshots",
    response_model=SnapshotJobResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "Token ausente o inválido"},
        404: {"model": ErrorResponse, "description": "Job no configurado"},
    },
)
def run_instagram_snapshots(
    use_case: CaptureInstagramFollowers = Depends(
        get_capture_instagram_followers_use_case
    ),
    settings: InstagramSettings = Depends(get_instagram_settings),
    x_job_token: Annotated[str | None, Header()] = None,
) -> SnapshotJobResponse:
    if not settings.instagram_snapshot_job_token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if not _job_token_matches(x_job_token, settings.instagram_snapshot_job_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    result = use_case.execute_all()
    return SnapshotJobResponse(captured=result.captured, failed=result.failed)


@router.post("/instagram/deauthorize", status_code=status.HTTP_200_OK)
def instagram_deauthorize(
    signed_request: Annotated[str, Form()],
    use_case: DeleteInstagramUserData = Depends(get_delete_instagram_user_data_use_case),
    settings: InstagramSettings = Depends(get_instagram_settings),
) -> dict[str, bool]:
    account_id = _instagram_user_id(signed_request, settings.instagram_app_secret)
    use_case.execute(account_id)
    return {"success": True}


@router.post("/instagram/data-deletion", status_code=status.HTTP_200_OK)
def instagram_data_deletion(
    signed_request: Annotated[str, Form()],
    use_case: DeleteInstagramUserData = Depends(get_delete_instagram_user_data_use_case),
    settings: InstagramSettings = Depends(get_instagram_settings),
) -> dict[str, str]:
    account_id = _instagram_user_id(signed_request, settings.instagram_app_secret)
    confirmation_code = use_case.execute(account_id)
    origin = public_site_origin(settings.instagram_redirect_uri)
    return {
        "url": f"{origin}/instagram/data-deletion/status?code={confirmation_code}",
        "confirmation_code": confirmation_code,
    }


@router.get("/instagram/data-deletion/status", status_code=status.HTTP_200_OK)
def instagram_data_deletion_status(code: str | None = None) -> dict[str, str]:
    return {
        "status": "completed",
        "confirmation_code": code or "",
    }


def _instagram_user_id(signed_request: str, app_secret: str) -> str:
    try:
        payload = parse_signed_request(signed_request, app_secret)
    except InvalidSignedRequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="signed_request inválido",
        ) from exc
    user_id = payload.get("user_id")
    if not isinstance(user_id, str) or not user_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="signed_request sin user_id",
        )
    return user_id.strip()


def _job_token_matches(provided: str | None, expected: str) -> bool:
    left = sha256((provided or "").encode("utf-8")).digest()
    right = sha256(expected.encode("utf-8")).digest()
    return hmac.compare_digest(left, right) and bool(provided)
