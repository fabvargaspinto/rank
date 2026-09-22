from pydantic import BaseModel, ConfigDict, Field


class UserLinkResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    type: str
    url: str
    sort_index: int


class UserResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(description="Id del usuario de negocio (public.users).")
    name: str | None = None
    avatar: str | None = None
    description: str | None = None
    links: list[UserLinkResponse] = Field(default_factory=list)


class UpdateUserLinkRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: str


class UpdateUserRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    avatar: str | None = None
    description: str | None = None
    links: list[UpdateUserLinkRequest] | None = None
