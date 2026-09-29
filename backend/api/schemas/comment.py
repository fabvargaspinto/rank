from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreateCommentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
    link: str | None = None


class CommentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    user_id: UUID
    text: str
    link: str | None = None
    created_at: datetime = Field(description="Fecha de creación en ISO 8601.")


class CommentListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[CommentResponse] = Field(default_factory=list)
    next_cursor: str | None = None
