from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Response, status

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
    get_user_by_name_use_case,
)
from controller.rate_limit import limiter
from core.comment.application.create_comment import CreateComment
from core.comment.application.delete_comment import DeleteComment
from core.comment.application.get_comments_by_user import (
    DEFAULT_LIMIT,
    MAX_LIMIT,
    GetCommentsByUser,
)
from core.comment.domain.comment import Comment
from core.comment.domain.comment_page import CommentPage
from core.user.application.get_user_by_name import GetUserByName
from core.user.domain.user import User

router = APIRouter()


def _to_response(comment: Comment) -> CommentResponse:
    return CommentResponse(
        id=comment.id.value,
        user_id=comment.user_id.value,
        text=comment.text.value,
        link=comment.link.value if comment.link else None,
        created_at=comment.created_at.value,
    )


@router.get(
    "/profiles/{username}/posts",
    response_model=CommentListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Usuario no encontrado",
        },
    },
)
def list_posts(
    username: str,
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
    cursor: Annotated[str | None, Query()] = None,
    users: GetUserByName = Depends(get_user_by_name_use_case),
    use_case: GetCommentsByUser = Depends(get_comments_by_user_use_case),
) -> CommentListResponse:
    user = users.execute(username)
    page = use_case.execute(user.id.value, limit=limit, cursor=cursor)
    return _page_response(page)


@router.post(
    "/me/posts",
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
        429: {
            "model": ErrorResponse,
            "description": "Demasiadas solicitudes",
        },
    },
)
@limiter.limit("20/minute")
def create_post(
    request: Request,
    body: CreateCommentRequest,
    profile: Annotated[User, Depends(get_current_profile)],
    use_case: CreateComment = Depends(get_create_comment_use_case),
) -> CommentResponse:
    return _to_response(
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
    use_case: DeleteComment = Depends(get_delete_comment_use_case),
) -> Response:
    use_case.execute(profile, str(post_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _page_response(page: CommentPage) -> CommentListResponse:
    return CommentListResponse(
        items=[_to_response(comment) for comment in page.items],
        next_cursor=page.next_cursor,
    )
