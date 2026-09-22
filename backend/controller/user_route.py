from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status

from api.dependencies.auth import CurrentUser, get_current_user
from api.schemas.auth import ErrorResponse
from api.schemas.user import AvatarUploadResponse, UpdateUserRequest, UserResponse
from config.dependency_container import (
    get_update_user_use_case,
    get_upload_avatar_use_case,
    get_user_by_name_use_case,
    get_user_use_case,
)
from core.user.application.application_error import UserNotFoundError
from core.user.application.get_user import GetUser
from core.user.application.get_user_by_name import GetUserByName
from core.user.application.update_user import UpdateUser
from core.user.application.upload_avatar import UploadAvatar
from core.user.domain.user import UNSET, User

router = APIRouter()


def _to_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id.value,
        name=user.name.value if user.name else None,
        avatar=user.avatar.value if user.avatar else None,
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
    response_model=UserResponse,
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
    use_case: GetUserByName = Depends(get_user_by_name_use_case),
) -> UserResponse:
    return _to_response(use_case.execute(username))


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
    use_case: GetUser = Depends(get_user_use_case),
) -> UserResponse:
    if auth_id != current_user.auth_id:
        raise UserNotFoundError("El usuario no existe")
    return _to_response(use_case.execute(auth_id))


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
    use_case: UpdateUser = Depends(get_update_user_use_case),
) -> UserResponse:
    if auth_id != current_user.auth_id:
        raise UserNotFoundError("El usuario no existe")
    return _to_response(
        use_case.execute(
            auth_id,
            name=body.name,
            avatar=(
                body.avatar
                if "avatar" in body.model_fields_set
                else UNSET
            ),
            description=body.description,
            links=(
                [link.url for link in body.links]
                if body.links is not None
                else None
            ),
        )
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
    use_case: UploadAvatar = Depends(get_upload_avatar_use_case),
    file: UploadFile = File(...),
) -> AvatarUploadResponse:
    if auth_id != current_user.auth_id:
        raise UserNotFoundError("El usuario no existe")

    content = file.file.read()
    url = use_case.execute(
        auth_id,
        content=content,
        content_type=file.content_type or "",
    )
    return AvatarUploadResponse(url=url)


