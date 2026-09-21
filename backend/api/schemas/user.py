from pydantic import BaseModel, ConfigDict, Field


class UserResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(description="Id del usuario de negocio (public.users).")
    name: str | None = None
    avatar: str | None = None
    description: str | None = None


class UpdateUserRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    avatar: str | None = None
    description: str | None = None
