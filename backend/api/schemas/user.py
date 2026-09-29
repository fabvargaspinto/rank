from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from api.schemas.comment import CommentResponse


class UserLinkResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    type: str
    url: str
    sort_index: int


class UserResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID = Field(description="Id del usuario de negocio (public.users).")
    name: str | None = None
    display_name: str | None = None
    avatar: str | None = None
    description: str | None = None
    links: list[UserLinkResponse] = Field(default_factory=list)


class PublicProfileResponse(UserResponse):
    comments: list[CommentResponse] = Field(default_factory=list)
    next_cursor: str | None = None


class UpdateUserLinkRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: str


class UpdateUserRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    display_name: str | None = None
    avatar: str | None = None
    description: str | None = None
    links: list[UpdateUserLinkRequest] | None = None


class AvatarUploadResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: str
