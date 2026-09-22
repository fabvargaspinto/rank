from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.dependencies.auth import CurrentUser, get_current_user
from api.schemas.auth import ErrorResponse
from api.schemas.comment import CommentResponse, CreateCommentRequest
from config.dependency_container import get_create_comment_use_case
from core.comment.application.create_comment import CreateComment
from core.comment.domain.comment import Comment
from core.user.application.application_error import UserNotFoundError

router = APIRouter()


def _to_response(comment: Comment) -> CommentResponse:
    return CommentResponse(
        id=comment.id.value,
        user_id=comment.user_id.value,
        text=comment.text.value,
        link=comment.link.value if comment.link else None,
        created_at=comment.created_at.to_isoformat(),
    )


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
    use_case: CreateComment = Depends(get_create_comment_use_case),
) -> CommentResponse:
    if auth_id != current_user.auth_id:
        raise UserNotFoundError("El usuario no existe")

    return _to_response(
        use_case.execute(
            auth_id,
            text=body.text,
            link=body.link,
        )
    )
