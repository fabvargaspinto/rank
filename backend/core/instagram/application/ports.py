from typing import Protocol

from core.instagram.domain.oauth_state import InstagramOAuthState


class TokenCipher(Protocol):
    def encrypt(self, token: str, *, associated_data: str) -> str:
        pass

    def decrypt(self, encrypted: str, *, associated_data: str) -> str:
        pass


class OAuthStateCodec(Protocol):
    def dumps(self, state: InstagramOAuthState) -> str:
        pass

    def loads(self, value: str) -> InstagramOAuthState:
        pass
