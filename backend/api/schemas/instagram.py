from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class InstagramConnectResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    authorization_url: str


class InstagramConnectionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    connected: bool
    username: str | None = None
    instagram_account_id: str | None = None
    avatar_url: str | None = None
    followers_count: int | None = None
    followers_delta: int | None = None


class FollowerHistoryItemResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    week_start: date
    followers_count: int
    captured_at: datetime
    delta: int | None = None


class FollowerHistoryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[FollowerHistoryItemResponse]


class SnapshotJobResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    captured: int
    failed: int


class CompleteInstagramOAuthRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str | None = None
    state: str | None = None
    error: str | None = None
