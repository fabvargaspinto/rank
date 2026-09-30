from collections.abc import Callable
from datetime import UTC, datetime
from secrets import token_urlsafe

from core.instagram.application.ports import OAuthStateCodec
from core.instagram.domain.instagram_graph import InstagramGraph
from core.instagram.domain.oauth_state import InstagramOAuthState
from core.instagram.domain.owner_user_id import OwnerUserId


class StartInstagramConnection:
    def __init__(
        self,
        graph: InstagramGraph,
        state_codec: OAuthStateCodec,
        nonce_factory: Callable[[], str] | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._graph = graph
        self._state_codec = state_codec
        self._nonce_factory = nonce_factory or (lambda: token_urlsafe(16))
        self._clock = clock or (lambda: datetime.now(UTC))

    def execute(self, owner_user_id: str) -> str:
        OwnerUserId(owner_user_id)
        state = InstagramOAuthState.issue(
            owner_user_id,
            self._nonce_factory(),
            self._clock(),
        )
        return self._graph.authorization_url(self._state_codec.dumps(state))
