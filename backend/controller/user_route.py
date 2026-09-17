from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.dependencies.auth import CurrentUser, get_current_user
from api.schemas.auth import ErrorResponse
from api.schemas.user import UserResponse
from config.dependency_container import get_user_by_name_use_case, get_user_use_case
from core.user.application.application_error import UserNotFoundError
from core.user.application.get_user import GetUser
from core.user.application.get_user_by_name import GetUserByName
from core.user.domain.user import User

router = APIRouter()


def _to_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id.value,
        name=user.name.value if user.name else None,
        avatar=user.avatar.value if user.avatar else None,
        description=user.description.value if user.description else None,
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
