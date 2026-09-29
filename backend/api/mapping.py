from api.schemas.post import PostListResponse, PostResponse
from api.schemas.user import UserLinkResponse, UserResponse
from core.post.domain.post import Post
from core.post.domain.post_page import PostPage
from core.user.application.update_user import UNSET
from core.user.domain.user import User
from core.user.infrastructure.avatar_url import object_path, public_avatar_url


def stored_avatar(avatar: str | None | object) -> str | None | object:
    if avatar is UNSET or avatar is None:
        return avatar
    if not isinstance(avatar, str) or not avatar.strip():
        return avatar
    return object_path(avatar)


def to_user_response(user: User, supabase_url: str) -> UserResponse:
    avatar = public_avatar_url(supabase_url, user.avatar.value) if user.avatar else None
    return UserResponse(
        id=user.id.value,
        name=user.name.value if user.name else None,
        display_name=user.display_name.value if user.display_name else None,
        avatar=avatar,
        description=user.description.value if user.description else None,
        links=[
            UserLinkResponse(
                id=link.id.value,
                type=link.type.value,
                url=link.url.value,
                sort_index=link.sort_index.value,
            )
            for link in user.links
        ],
    )


def to_post_response(post: Post) -> PostResponse:
    return PostResponse(
        id=post.id.value,
        user_id=post.user_id.value,
        text=post.text.value,
        link=post.link.value if post.link else None,
        created_at=post.created_at.value,
    )


def to_post_page(page: PostPage) -> PostListResponse:
    return PostListResponse(
        items=[to_post_response(post) for post in page.items],
        next_cursor=page.next_cursor,
    )
