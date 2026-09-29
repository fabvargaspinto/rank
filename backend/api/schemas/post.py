from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreatePostRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
    link: str | None = None


class PostResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    user_id: UUID
    text: str
    link: str | None = None
    created_at: datetime = Field(description="Fecha de creación en ISO 8601.")


class PostListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[PostResponse] = Field(default_factory=list)
    next_cursor: str | None = None
