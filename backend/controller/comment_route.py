from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status

from api.dependencies.auth import CurrentUser, get_current_user
from api.dependencies.current_profile import get_current_profile
from api.schemas.auth import ErrorResponse
from api.schemas.comment import (
    CommentListResponse,
    CommentResponse,
    CreateCommentRequest,
)
from config.dependency_container import (
    get_comments_by_user_use_case,
    get_create_comment_use_case,
    get_delete_comment_use_case,
)
from core.comment.application.create_comment import CreateComment
from core.comment.application.delete_comment import DeleteComment
from core.comment.application.get_comments_by_user import (
    DEFAULT_LIMIT,
    MAX_LIMIT,
    GetCommentsByUser,
)
from core.comment.domain.comment import Comment
from core.comment.domain.comment_page import CommentPage
from core.user.application.application_error import UserNotFoundError
from core.user.domain.user import User

router = APIRouter()


def _to_response(comment: Comment) -> CommentResponse:
    return CommentResponse(
        id=comment.id.value,
        user_id=comment.user_id.value,
        text=comment.text.value,
        link=comment.link.value if comment.link else None,
        created_at=comment.created_at.to_isoformat(),
    )


@router.get(
    "/users/id/{user_id}/comments",
    response_model=CommentListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Usuario no encontrado",
        },
    },
)
def list_comments_by_user(
    user_id: UUID,
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
    cursor: Annotated[str | None, Query()] = None,
    use_case: GetCommentsByUser = Depends(get_comments_by_user_use_case),
) -> CommentListResponse:
    page = use_case.execute(str(user_id), limit=limit, cursor=cursor)
    return _page_response(page)


@router.post(
    "/users/{auth_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Token ausente o inválido",
        },
        400: {
            "model": ErrorResponse,
            "description": "Comentario inválido",
        },
        404: {
            "model": ErrorResponse,
            "description": "Usuario no encontrado",
        },
    },
)
def create_comment(
    auth_id: str,
    body: CreateCommentRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    profile: Annotated[User, Depends(get_current_profile)],
    use_case: CreateComment = Depends(get_create_comment_use_case),
) -> CommentResponse:
    if auth_id != current_user.auth_id:
        raise UserNotFoundError("El usuario no existe")

    return _to_response(
        use_case.execute(
            profile,
            text=body.text,
            link=body.link,
        )
    )


@router.delete(
    "/users/{auth_id}/comments/{comment_id}",
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
def delete_comment(
    auth_id: str,
    comment_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    profile: Annotated[User, Depends(get_current_profile)],
    use_case: DeleteComment = Depends(get_delete_comment_use_case),
) -> Response:
    if auth_id != current_user.auth_id:
        raise UserNotFoundError("El usuario no existe")

    use_case.execute(profile, str(comment_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _page_response(page: CommentPage) -> CommentListResponse:
    return CommentListResponse(
        items=[_to_response(comment) for comment in page.items],
        next_cursor=page.next_cursor,
    )
