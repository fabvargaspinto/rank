from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from core.instagram.domain.errors import (
    InstagramOAuthStateExpiredError,
    InvalidOAuthNonceError,
)
from core.instagram.domain.owner_user_id import OwnerUserId


@dataclass(frozen=True)
class InstagramOAuthState:
    owner_user_id: OwnerUserId
    nonce: str
    expires_at: datetime

    TTL = timedelta(minutes=10)

    def __post_init__(self) -> None:
        if not isinstance(self.nonce, str) or not self.nonce.strip():
            raise InvalidOAuthNonceError("El estado de OAuth no es válido")
        if self.expires_at.tzinfo is None or self.expires_at.utcoffset() is None:
            raise InvalidOAuthNonceError("El estado de OAuth no es válido")
        object.__setattr__(self, "nonce", self.nonce.strip())

    @staticmethod
    def create(
        owner_user_id: str,
        nonce: str,
        expires_at: datetime,
    ) -> "InstagramOAuthState":
        return InstagramOAuthState(
            owner_user_id=OwnerUserId(owner_user_id),
            nonce=nonce,
            expires_at=expires_at,
        )

    @classmethod
    def issue(
        cls,
        owner_user_id: str,
        nonce: str,
        now: datetime | None = None,
    ) -> "InstagramOAuthState":
        moment = now or datetime.now(UTC)
        return cls.create(owner_user_id, nonce, moment + cls.TTL)

    def ensure_valid(self, now: datetime | None = None) -> None:
        moment = now or datetime.now(UTC)
        if moment >= self.expires_at:
            raise InstagramOAuthStateExpiredError(
                "El inicio de sesión de Instagram expiró"
            )
