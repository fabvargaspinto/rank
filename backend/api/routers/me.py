from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Request, Response, UploadFile, status

from api.dependencies.auth import CurrentUser, get_current_user
from api.dependencies.container import (
    get_create_post_use_case,
    get_delete_account_use_case,
    get_delete_post_use_case,
    get_update_user_use_case,
    get_upload_avatar_use_case,
)
from api.dependencies.current_profile import get_current_profile
from api.dependencies.supabase import get_supabase_url
from api.mapping import to_post_response, to_user_response
from api.rate_limit import limiter
from api.schemas.auth import ErrorResponse
from api.schemas.post import CreatePostRequest, PostResponse
from api.schemas.user import AvatarUploadResponse, UpdateUserRequest, UserResponse
from core.post.application.create_post import CreatePost
from core.post.application.delete_post import DeletePost
from core.user.application.application_error import InvalidAvatarFileError
from core.user.application.delete_account import DeleteAccount
from core.user.application.update_user import UNSET, UpdateProfileCommand, UpdateUser
from core.user.application.upload_avatar import MAX_AVATAR_BYTES, UploadAvatar
from core.user.domain.user import User
from core.user.infrastructure.avatar_url import public_avatar_url

router = APIRouter()


def _read_upload(upload: UploadFile) -> bytes:
    content = upload.file.read(MAX_AVATAR_BYTES + 1)
    if len(content) > MAX_AVATAR_BYTES:
        raise InvalidAvatarFileError("La imagen no puede superar 2 MB")
    return content


@router.get(
    "/me",
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
def read_me(
    profile: Annotated[User, Depends(get_current_profile)],
    supabase_url: str = Depends(get_supabase_url),
) -> UserResponse:
    return to_user_response(profile, supabase_url)


@router.patch(
    "/me",
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
        429: {
            "model": ErrorResponse,
            "description": "Demasiadas solicitudes",
        },
    },
)
@limiter.limit("30/minute")
def update_me(
    request: Request,
    body: UpdateUserRequest,
    profile: Annotated[User, Depends(get_current_profile)],
    use_case: UpdateUser = Depends(get_update_user_use_case),
    supabase_url: str = Depends(get_supabase_url),
) -> UserResponse:
    display_name = (
        body.display_name if "display_name" in body.model_fields_set else UNSET
    )
    return to_user_response(
        use_case.execute(
            profile,
            UpdateProfileCommand(
                name=body.name,
                display_name=display_name,
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


@router.put(
    "/me/avatar",
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
        429: {
            "model": ErrorResponse,
            "description": "Demasiadas solicitudes",
        },
    },
)
@limiter.limit("10/minute")
def upload_avatar(
    request: Request,
    profile: Annotated[User, Depends(get_current_profile)],
    use_case: UploadAvatar = Depends(get_upload_avatar_use_case),
    supabase_url: str = Depends(get_supabase_url),
    file: UploadFile = File(...),
) -> AvatarUploadResponse:
    path = use_case.execute(profile, _read_upload(file))
    return AvatarUploadResponse(url=public_avatar_url(supabase_url, path))


@router.delete(
    "/me",
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
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    use_case: DeleteAccount = Depends(get_delete_account_use_case),
) -> Response:
    use_case.execute(current_user.auth_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/me/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Token ausente o inválido",
        },
        400: {
            "model": ErrorResponse,
            "description": "Publicación inválida",
        },
        404: {
            "model": ErrorResponse,
            "description": "Usuario no encontrado",
        },
        429: {
            "model": ErrorResponse,
            "description": "Demasiadas solicitudes",
        },
    },
)
@limiter.limit("20/minute")
def create_post(
    request: Request,
    body: CreatePostRequest,
    profile: Annotated[User, Depends(get_current_profile)],
    use_case: CreatePost = Depends(get_create_post_use_case),
) -> PostResponse:
    return to_post_response(
        use_case.execute(
            profile,
            text=body.text,
            link=body.link,
        )
    )


@router.delete(
    "/me/posts/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Token ausente o inválido",
        },
        404: {
            "model": ErrorResponse,
            "description": "Publicación no encontrada",
        },
    },
)
def delete_post(
    post_id: UUID,
    profile: Annotated[User, Depends(get_current_profile)],
    use_case: DeletePost = Depends(get_delete_post_use_case),
) -> Response:
    use_case.execute(profile, str(post_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
