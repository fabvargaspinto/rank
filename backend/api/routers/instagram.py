import hmac
from hashlib import sha256
from typing import Annotated
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse

from api.dependencies.container import (
    get_capture_instagram_followers_use_case,
    get_complete_instagram_oauth_use_case,
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
from core.instagram.application.disconnect_instagram import DisconnectInstagram
from core.instagram.application.get_follower_history import GetFollowerHistory
from core.instagram.application.get_instagram_connection import GetInstagramConnection
from core.instagram.application.start_instagram_connection import (
    StartInstagramConnection,
)
from core.shared.application.application_error import ApplicationError
from core.shared.domain.domain_error import DomainError
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


@router.get(
    "/instagram/oauth/callback",
    status_code=status.HTTP_302_FOUND,
    response_class=RedirectResponse,
)
def instagram_oauth_callback(
    use_case: CompleteInstagramOAuth = Depends(get_complete_instagram_oauth_use_case),
    settings: InstagramSettings = Depends(get_instagram_settings),
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
) -> RedirectResponse:
    frontend = settings.frontend_url.rstrip("/")
    try:
        use_case.execute(state or "", code, error)
    except (ApplicationError, DomainError):
        return RedirectResponse(
            f"{frontend}/dashboard/tree?{urlencode({'instagram': 'error'})}",
            status_code=status.HTTP_302_FOUND,
        )
    return RedirectResponse(
        f"{frontend}/dashboard/tree?{urlencode({'instagram': 'connected'})}",
        status_code=status.HTTP_302_FOUND,
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


def _job_token_matches(provided: str | None, expected: str) -> bool:
    left = sha256((provided or "").encode("utf-8")).digest()
    right = sha256(expected.encode("utf-8")).digest()
    return hmac.compare_digest(left, right) and bool(provided)
