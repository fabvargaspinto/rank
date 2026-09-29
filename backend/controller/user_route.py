from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, Response, UploadFile, status

from api.dependencies.auth import CurrentUser, get_current_user
from api.dependencies.current_profile import get_current_profile
from api.schemas.auth import ErrorResponse
from api.schemas.comment import CommentResponse
from api.schemas.user import (
    AvatarUploadResponse,
    PublicProfileResponse,
    UpdateUserRequest,
    UserResponse,
)
from config.db_settings import DBSettings
from config.dependency_container import (
    get_delete_account_use_case,
    get_public_profile_use_case,
    get_update_user_use_case,
    get_upload_avatar_use_case,
)
from core.comment.application.get_comments_by_user import (
    DEFAULT_LIMIT,
    MAX_LIMIT,
)
from core.user.application.application_error import UserNotFoundError
from core.user.application.delete_account import DeleteAccount
from core.user.application.get_public_profile import GetPublicProfile
from core.user.application.update_user import UNSET, UpdateProfileCommand, UpdateUser
from core.user.application.upload_avatar import UploadAvatar
from core.user.domain.user import User
from core.user.infrastructure.avatar_url import object_path, public_avatar_url

router = APIRouter()


def get_supabase_url() -> str:
    return DBSettings().supabase_url.rstrip("/")


def _stored_avatar(avatar: str | None | object) -> str | None | object:
    if avatar is UNSET or avatar is None:
        return avatar
    if not isinstance(avatar, str) or not avatar.strip():
        return avatar
    return object_path(avatar)


def _to_response(user: User, supabase_url: str) -> UserResponse:
    avatar = (
        public_avatar_url(supabase_url, user.avatar.value) if user.avatar else None
    )
    return UserResponse(
        id=user.id.value,
        name=user.name.value if user.name else None,
        display_name=user.display_name.value if user.display_name else None,
        avatar=avatar,
        description=user.description.value if user.description else None,
        links=[
            {
                "id": link.id.value,
                "type": link.type.value,
                "url": link.url.value,
                "sort_index": link.sort_index.value,
            }
            for link in user.links
        ],
    )


@router.get(
    "/users/name/{username}",
    response_model=PublicProfileResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Usuario no encontrado",
        },
    },
)
def read_user_by_name(
    username: str,
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
    use_case: GetPublicProfile = Depends(get_public_profile_use_case),
    supabase_url: str = Depends(get_supabase_url),
) -> PublicProfileResponse:
    profile = use_case.execute(username, limit=limit)
    user = _to_response(profile.user, supabase_url)
    return PublicProfileResponse(
        **user.model_dump(),
        comments=[
            CommentResponse(
                id=comment.id.value,
                user_id=comment.user_id.value,
                text=comment.text.value,
                link=comment.link.value if comment.link else None,
                created_at=comment.created_at.to_isoformat(),
            )
            for comment in profile.comments
        ],
        next_cursor=profile.next_cursor,
    )


@router.get(
    "/users/{auth_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Token ausente o inválido",
        },
        404: {
            "model": ErrorResponse,
            "description": "Usuario no encontrado",
        },
    },
)
def read_user_by_auth_id(
    auth_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    profile: Annotated[User, Depends(get_current_profile)],
    supabase_url: str = Depends(get_supabase_url),
) -> UserResponse:
    if auth_id != current_user.auth_id:
        raise UserNotFoundError("El usuario no existe")
    return _to_response(profile, supabase_url)


@router.patch(
    "/users/{auth_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Token ausente o inválido",
        },
        404: {
            "model": ErrorResponse,
            "description": "Usuario no encontrado",
        },
        409: {
            "model": ErrorResponse,
            "description": "El nombre ya está en uso",
        },
    },
)
def update_user(
    auth_id: str,
    body: UpdateUserRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    profile: Annotated[User, Depends(get_current_profile)],
    use_case: UpdateUser = Depends(get_update_user_use_case),
    supabase_url: str = Depends(get_supabase_url),
) -> UserResponse:
    if auth_id != current_user.auth_id:
        raise UserNotFoundError("El usuario no existe")
    avatar = (
        body.avatar
        if "avatar" in body.model_fields_set
        else UNSET
    )
    display_name = (
        body.display_name
        if "display_name" in body.model_fields_set
        else UNSET
    )
    return _to_response(
        use_case.execute(
            profile,
            UpdateProfileCommand(
                name=body.name,
                display_name=display_name,
                avatar=_stored_avatar(avatar),
                description=body.description,
                links=(
                    [link.url for link in body.links]
                    if body.links is not None
                    else None
                ),
            ),
        ),
        supabase_url,
    )


@router.post(
    "/users/{auth_id}/avatar",
    response_model=AvatarUploadResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Token ausente o inválido",
        },
        400: {
            "model": ErrorResponse,
            "description": "Archivo de imagen inválido",
        },
        404: {
            "model": ErrorResponse,
            "description": "Usuario no encontrado",
        },
    },
)
def upload_avatar(
    auth_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    profile: Annotated[User, Depends(get_current_profile)],
    use_case: UploadAvatar = Depends(get_upload_avatar_use_case),
    supabase_url: str = Depends(get_supabase_url),
    file: UploadFile = File(...),
) -> AvatarUploadResponse:
    if auth_id != current_user.auth_id:
        raise UserNotFoundError("El usuario no existe")

    content = file.file.read()
    path = use_case.execute(profile, current_user.auth_id, content)
    return AvatarUploadResponse(url=public_avatar_url(supabase_url, path))


@router.delete(
    "/users/{auth_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Token ausente o inválido",
        },
        404: {
            "model": ErrorResponse,
            "description": "Usuario no encontrado",
        },
    },
)
def delete_account(
    auth_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    use_case: DeleteAccount = Depends(get_delete_account_use_case),
) -> Response:
    if auth_id != current_user.auth_id:
        raise UserNotFoundError("El usuario no existe")
    use_case.execute(auth_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


