from pydantic import BaseModel


class SessionResponse(BaseModel):
    provisioned: bool
