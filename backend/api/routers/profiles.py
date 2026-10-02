from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status

from api.dependencies.container import (
    get_posts_by_user_use_case,
    get_public_profile_use_case,
    get_user_by_name_use_case,
)
from api.dependencies.supabase import get_supabase_url
from api.mapping import to_post_page, to_post_response, to_user_response
from api.rate_limit import limiter
from api.schemas.auth import ErrorResponse
from api.schemas.post import PostListResponse
from api.schemas.user import PublicProfileResponse
from core.post.application.get_posts_by_user import (
    DEFAULT_LIMIT,
    MAX_LIMIT,
    GetPostsByUser,
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
        429: {
            "model": ErrorResponse,
            "description": "Demasiadas solicitudes",
        },
    },
)
@limiter.limit("60/minute")
def read_profile(
    request: Request,
    username: str,
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
    use_case: GetPublicProfile = Depends(get_public_profile_use_case),
    supabase_url: str = Depends(get_supabase_url),
) -> PublicProfileResponse:
    profile = use_case.execute(username, limit=limit)
    user = to_user_response(profile.user, supabase_url)
    return PublicProfileResponse(
        **user.model_dump(),
        posts=[to_post_response(post) for post in profile.posts],
        next_cursor=profile.next_cursor,
    )


@router.get(
    "/profiles/{username}/posts",
    response_model=PostListResponse,
    status_code=status.HTTP_200_OK,
    responses={
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
@limiter.limit("60/minute")
def list_posts(
    request: Request,
    username: str,
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
    cursor: Annotated[str | None, Query()] = None,
    users: GetUserByName = Depends(get_user_by_name_use_case),
    use_case: GetPostsByUser = Depends(get_posts_by_user_use_case),
) -> PostListResponse:
    user = users.execute(username)
    page = use_case.execute(user.id.value, limit=limit, cursor=cursor)
    return to_post_page(page)
