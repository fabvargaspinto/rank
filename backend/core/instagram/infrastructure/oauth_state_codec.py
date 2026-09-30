from __future__ import annotations

import hmac
from base64 import urlsafe_b64decode, urlsafe_b64encode
from datetime import UTC, datetime
from hashlib import sha256

from config.instagram_settings import InstagramSettings
from core.instagram.application.application_error import InstagramOAuthStateError
from core.instagram.domain.oauth_state import InstagramOAuthState


class SignedOAuthStateCodec:
    def __init__(self, settings: InstagramSettings) -> None:
        self._key = settings.token_encryption_key_bytes

    def dumps(self, state: InstagramOAuthState) -> str:
        payload = (
            f"{state.owner_user_id.value}:{state.nonce}:"
            f"{int(state.expires_at.timestamp())}"
        )
        body = _b64(payload.encode("utf-8"))
        signature = _b64(self._sign(body.encode("ascii")))
        return f"{body}.{signature}"

    def loads(self, value: str) -> InstagramOAuthState:
        try:
            body, signature = value.split(".", 1)
        except ValueError as exc:
            raise InstagramOAuthStateError(
                "El inicio de sesión de Instagram no es válido"
            ) from exc

        expected = _b64(self._sign(body.encode("ascii")))
        if not hmac.compare_digest(signature, expected):
            raise InstagramOAuthStateError(
                "El inicio de sesión de Instagram no es válido"
            )

        try:
            decoded = urlsafe_b64decode(_pad(body)).decode("utf-8")
            owner_user_id, nonce, expires = decoded.split(":", 2)
            expires_at = datetime.fromtimestamp(int(expires), tz=UTC)
        except (ValueError, UnicodeDecodeError) as exc:
            raise InstagramOAuthStateError(
                "El inicio de sesión de Instagram no es válido"
            ) from exc

        return InstagramOAuthState.create(owner_user_id, nonce, expires_at)

    def _sign(self, body: bytes) -> bytes:
        return hmac.new(self._key, body, sha256).digest()


def _b64(value: bytes) -> str:
    return urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _pad(value: str) -> bytes:
    padded = value + ("=" * (-len(value) % 4))
    return padded.encode("ascii")
