from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from api.dependencies.container import (
    get_comments_by_user_use_case,
    get_public_profile_use_case,
    get_user_by_name_use_case,
)
from api.dependencies.supabase import get_supabase_url
from api.mapping import to_comment_page, to_comment_response, to_user_response
from api.schemas.auth import ErrorResponse
from api.schemas.comment import CommentListResponse
from api.schemas.user import PublicProfileResponse
from core.comment.application.get_comments_by_user import (
    DEFAULT_LIMIT,
    MAX_LIMIT,
    GetCommentsByUser,
)
from core.user.application.get_public_profile import GetPublicProfile
from core.user.application.get_user_by_name import GetUserByName

router = APIRouter()


@router.get(
    "/profiles/{username}",
    response_model=PublicProfileResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Usuario no encontrado",
        },
    },
)
def read_profile(
    username: str,
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
    use_case: GetPublicProfile = Depends(get_public_profile_use_case),
    supabase_url: str = Depends(get_supabase_url),
) -> PublicProfileResponse:
    profile = use_case.execute(username, limit=limit)
    user = to_user_response(profile.user, supabase_url)
    return PublicProfileResponse(
        **user.model_dump(),
        comments=[to_comment_response(comment) for comment in profile.comments],
        next_cursor=profile.next_cursor,
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
    return to_comment_page(page)
