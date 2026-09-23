from pydantic import BaseModel, ConfigDict, Field


class CreateCommentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
    link: str | None = None


class CommentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    user_id: str
    text: str
    link: str | None = None
    created_at: str = Field(description="Fecha de creación en ISO 8601.")


class CommentListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[CommentResponse] = Field(default_factory=list)
