from pydantic import BaseModel, ConfigDict, Field


class SessionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provisioned: bool = Field(
        description="True si el usuario local y su identidad quedaron aprovisionados.",
    )


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    detail: str
