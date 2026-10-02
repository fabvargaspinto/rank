from collections.abc import Callable
from datetime import UTC, datetime
from logging import getLogger

from core.instagram.application.application_error import (
    InstagramAccountAlreadyLinkedError,
    InstagramOAuthDeniedError,
    InstagramOAuthStateError,
)
from core.instagram.application.capture_instagram_followers import (
    CaptureInstagramFollowers,
)
from core.instagram.application.ports import OAuthStateCodec, TokenCipher
from core.instagram.domain.instagram_connection import InstagramConnection
from core.instagram.domain.instagram_connection_repo import (
    InstagramConnectionRepository,
    StoredInstagramConnection,
)
from core.instagram.domain.instagram_graph import InstagramGraph
from core.instagram.domain.oauth_state import InstagramOAuthState

logger = getLogger("ig.instagram.oauth")


class CompleteInstagramOAuth:
    def __init__(
        self,
        graph: InstagramGraph,
        connections: InstagramConnectionRepository,
        cipher: TokenCipher,
        state_codec: OAuthStateCodec,
        capture: CaptureInstagramFollowers,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._graph = graph
        self._connections = connections
        self._cipher = cipher
        self._state_codec = state_codec
        self._capture = capture
        self._clock = clock or (lambda: datetime.now(UTC))

    def execute(
        self,
        owner_user_id: str,
        state: str,
        code: str | None,
        error: str | None = None,
    ) -> InstagramConnection:
        if error or not code or not code.strip():
            raise InstagramOAuthDeniedError(
                "No se pudo conectar Instagram. Volvé a intentarlo."
            )
        if not state or not state.strip():
            raise InstagramOAuthStateError(
                "El inicio de sesión de Instagram no es válido"
            )

        payload = self._parse_state(state.strip())
        payload.ensure_valid(self._clock())
        if payload.owner_user_id.value.lower() != owner_user_id.strip().lower():
            raise InstagramOAuthStateError(
                "El inicio de sesión de Instagram no es válido"
            )
        login = self._graph.complete_login(code.strip())

        linked = self._connections.get_by_account(login.account.id.value)
        if linked is not None and not linked.connection.belongs_to(
            payload.owner_user_id.value
        ):
            raise InstagramAccountAlreadyLinkedError(
                "Esa cuenta de Instagram ya está conectada a otro usuario"
            )

        existing = self._connections.get_by_owner(payload.owner_user_id.value)
        avatar_url = (
            login.account.avatar_url.value
            if login.account.avatar_url is not None
            else None
        )
        if existing is None:
            connection = InstagramConnection.connect(
                payload.owner_user_id.value,
                login.account.id.value,
                login.account.username.value,
                login.token.expires_at,
                avatar_url,
            )
        else:
            connection = existing.connection.reauthorize(
                login.account.id.value,
                login.account.username.value,
                login.token.expires_at,
                avatar_url,
            )

        self._connections.save(
            StoredInstagramConnection(
                connection=connection,
                access_token_encrypted=self._cipher.encrypt(
                    login.token.value,
                    associated_data=connection.id.value,
                ),
            )
        )
        try:
            self._capture.execute_for_owner(payload.owner_user_id.value)
        except Exception:
            logger.exception(
                "instagram_initial_snapshot_failed",
                extra={"owner_user_id": payload.owner_user_id.value},
            )
        return connection

    def _parse_state(self, state: str) -> InstagramOAuthState:
        try:
            return self._state_codec.loads(state)
        except InstagramOAuthStateError:
            raise
        except Exception as exc:
            raise InstagramOAuthStateError(
                "El inicio de sesión de Instagram no es válido"
            ) from exc
