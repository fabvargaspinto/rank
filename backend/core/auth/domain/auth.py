from dataclasses import dataclass
from datetime import datetime

from core.auth.domain.auth_created_at import AuthCreatedAt
from core.auth.domain.auth_email import AuthEmail
from core.auth.domain.auth_id import AuthId
from core.user.domain.user_id import UserId


@dataclass(frozen=True)
class Auth:
    id: AuthId
    user_id: UserId
    email: AuthEmail
    created_at: AuthCreatedAt

    @staticmethod
    def create(user_id: str, email: str) -> "Auth":
        return Auth(
            id=AuthId.generate(),
            user_id=UserId(user_id),
            email=AuthEmail(email),
            created_at=AuthCreatedAt.now(),
        )

    @staticmethod
    def from_primitive(primitive: dict, email: AuthEmail) -> "Auth":
        

        return Auth(
            id=AuthId(primitive["id"]),
            user_id=UserId(primitive["user_id"]),
            email=email,
            created_at=AuthCreatedAt.from_isoformat(primitive["created_at"]),
        )
