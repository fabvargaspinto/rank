from uuid import uuid4

import pytest
from postgrest.exceptions import APIError

from core.auth.domain.auth import Auth
from core.auth.domain.auth_email import AuthEmail
from core.auth.domain.auth_error import IdentityAlreadyExistsError
from core.auth.domain.auth_provider import AuthProvider
from core.auth.infrastructure.auth_supabase_repo import AuthSupabaseRepo
from core.auth.infrastructure.email_crypto import EmailCrypto
from core.user.domain.user import User
from db.db_client import DBClient

_PASSWORD = "Password123"


class _TrackedRows:
    def __init__(self) -> None:
        self.auth_ids: list[str] = []
        self.user_ids: list[str] = []

    def add(self, auth_id: str, user_id: str | None = None) -> None:
        self.auth_ids.append(auth_id)
        if user_id is not None:
            self.user_ids.append(user_id)


@pytest.fixture
def tracked_rows(db_client: DBClient):
    tracked = _TrackedRows()
    yield tracked
    supabase = db_client.get_db()
    for auth_id in tracked.auth_ids:
        try:
            supabase.table("auth").delete().eq("id", auth_id).execute()
        except APIError:
            pass
        try:
            supabase.auth.admin.delete_user(auth_id)
        except Exception:
            pass
    for user_id in tracked.user_ids:
        try:
            supabase.table("users").delete().eq("id", user_id).execute()
        except APIError:
            pass


def _unique_email(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex}@example.com"


def _create_idp_user(db_client: DBClient, email: str) -> str:
    created = db_client.get_db().auth.admin.create_user({
        "email": email,
        "password": _PASSWORD,
        "email_confirm": True,
    })
    assert created.user is not None
    return created.user.id


def _new_user_and_auth(auth_id: str, email: str) -> tuple[User, Auth]:
    user = User.create_empty()
    auth = Auth.create_with_email(
        id=auth_id,
        user_id=user.id.value,
        email=email,
    )
    return user, auth


def test_save_creates_user_and_auth_via_rpc(
    auth_repo: AuthSupabaseRepo,
    db_client: DBClient,
    tracked_rows: _TrackedRows,
) -> None:
    email = _unique_email("repo-save")
    auth_id = _create_idp_user(db_client, email)
    user, auth = _new_user_and_auth(auth_id, email)
    tracked_rows.add(auth_id, user.id.value)

    saved = auth_repo.save(user, auth)

    supabase = db_client.get_db()
    auth_row = (
        supabase.table("auth")
        .select("id,user_id,provider")
        .eq("id", auth_id)
        .execute()
    )
    user_row = (
        supabase.table("users")
        .select("id")
        .eq("id", user.id.value)
        .execute()
    )

    assert saved.id.value == auth_id
    assert saved.user_id.value == user.id.value
    assert saved.provider_method.provider is AuthProvider.EMAIL
    assert auth_row.data == [{
        "id": auth_id,
        "user_id": user.id.value,
        "provider": "EMAIL",
    }]
    assert user_row.data == [{"id": user.id.value}]


def test_save_then_find_by_email_recovers_email(
    auth_repo: AuthSupabaseRepo,
    db_client: DBClient,
    tracked_rows: _TrackedRows,
) -> None:
    email = _unique_email("repo-find")
    auth_id = _create_idp_user(db_client, email)
    user, auth = _new_user_and_auth(auth_id, email.upper())
    tracked_rows.add(auth_id, user.id.value)

    auth_repo.save(user, auth)
    found = auth_repo.find_by_email(email.upper())

    assert found is not None
    assert found.id.value == auth_id
    assert found.email.value == email
    assert found.user_id.value == user.id.value


def test_email_is_encrypted_with_aes_gcm(
    auth_repo: AuthSupabaseRepo,
    email_crypto: EmailCrypto,
    db_client: DBClient,
    tracked_rows: _TrackedRows,
) -> None:
    email = _unique_email("repo-aes")
    auth_id = _create_idp_user(db_client, email)
    user, auth = _new_user_and_auth(auth_id, email)
    tracked_rows.add(auth_id, user.id.value)

    first_ciphertext = email_crypto.encrypt(AuthEmail(email))
    second_ciphertext = email_crypto.encrypt(AuthEmail(email))
    assert first_ciphertext != second_ciphertext
    assert email_crypto.decrypt(first_ciphertext).value == email

    auth_repo.save(user, auth)

    row = (
        db_client.get_db()
        .table("auth")
        .select("email_encrypted")
        .eq("id", auth_id)
        .execute()
    )
    stored = row.data[0]["email_encrypted"]

    assert stored != email
    assert email not in stored
    assert email_crypto.decrypt(stored).value == email


def test_find_by_email_uses_hmac(
    auth_repo: AuthSupabaseRepo,
    email_crypto: EmailCrypto,
    db_client: DBClient,
    tracked_rows: _TrackedRows,
) -> None:
    email = _unique_email("repo-hmac")
    auth_id = _create_idp_user(db_client, email)
    user, auth = _new_user_and_auth(auth_id, email)
    tracked_rows.add(auth_id, user.id.value)

    auth_repo.save(user, auth)

    row = (
        db_client.get_db()
        .table("auth")
        .select("email_hmac")
        .eq("id", auth_id)
        .execute()
    )
    expected_hmac = email_crypto.hmac(AuthEmail(email))

    assert row.data[0]["email_hmac"] == expected_hmac
    assert auth_repo.find_by_email(email) is not None
    assert auth_repo.find_by_email(_unique_email("repo-hmac-miss")) is None


def test_duplicate_email_raises_identity_already_exists(
    auth_repo: AuthSupabaseRepo,
    db_client: DBClient,
    tracked_rows: _TrackedRows,
) -> None:
    shared_email = _unique_email("repo-dup")
    first_idp = _unique_email("repo-dup-a")
    second_idp = _unique_email("repo-dup-b")

    first_auth_id = _create_idp_user(db_client, first_idp)
    first_user, first_auth = _new_user_and_auth(first_auth_id, shared_email)
    tracked_rows.add(first_auth_id, first_user.id.value)
    auth_repo.save(first_user, first_auth)

    second_auth_id = _create_idp_user(db_client, second_idp)
    second_user, second_auth = _new_user_and_auth(second_auth_id, shared_email)
    tracked_rows.add(second_auth_id, second_user.id.value)

    with pytest.raises(IdentityAlreadyExistsError):
        auth_repo.save(second_user, second_auth)

    assert auth_repo.find_by_email(shared_email).id.value == first_auth_id
    assert auth_repo.find_by_id(second_auth_id) is None
