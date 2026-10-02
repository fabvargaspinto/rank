from uuid import uuid4

from postgrest.exceptions import APIError
from uuid6 import uuid7

from core.shared.infrastructure.supabase_client import DBClient


def _assert_no_rows(execute):
    try:
        response = execute()
    except APIError:
        return
    assert response.data == [] or response.data is None


def test_anon_cannot_read_users(anon_client) -> None:
    _assert_no_rows(lambda: anon_client.table("users").select("id").limit(1).execute())


def test_anon_cannot_read_auth(anon_client) -> None:
    _assert_no_rows(lambda: anon_client.table("auth").select("id").limit(1).execute())


def test_anon_cannot_write_users(anon_client) -> None:
    user_id = str(uuid7())
    try:
        response = anon_client.table("users").insert({"id": user_id}).execute()
    except APIError:
        return
    assert not response.data


def test_anon_cannot_execute_create_user_and_auth(anon_client) -> None:
    try:
        anon_client.rpc(
            "create_user_and_auth",
            {
                "p_user_id": str(uuid7()),
                "p_auth_id": str(uuid7()),
                "p_email_encrypted": "x",
                "p_email_hmac": "x",
                "p_provider": "EMAIL",
                "p_provider_id": None,
            },
        ).execute()
    except APIError:
        return
    raise AssertionError("anon no debería ejecutar create_user_and_auth")


def test_authenticated_cannot_update_own_profile(
    db_client: DBClient, anon_client
) -> None:
    supabase = db_client.get_db()
    password = "Password123"
    email = f"rls-write-{uuid4().hex}@example.com"
    created = supabase.auth.admin.create_user(
        {
            "email": email,
            "password": password,
            "email_confirm": True,
        }
    )
    assert created.user is not None
    auth_id = created.user.id
    user_id = str(uuid7())

    try:
        supabase.rpc(
            "create_user_and_auth",
            {
                "p_user_id": user_id,
                "p_auth_id": auth_id,
                "p_email_encrypted": "rls-write",
                "p_email_hmac": f"rls-write-{uuid4().hex}",
                "p_provider": "EMAIL",
                "p_provider_id": None,
            },
        ).execute()
        signed_in = anon_client.auth.sign_in_with_password(
            {
                "email": email,
                "password": password,
            }
        )
        assert signed_in.user is not None

        try:
            response = (
                anon_client.table("users")
                .update({"name": "phish"})
                .eq("id", user_id)
                .execute()
            )
        except APIError:
            return
        assert not response.data
    finally:
        try:
            anon_client.auth.sign_out()
        except Exception:
            pass
        supabase.table("auth").delete().eq("id", auth_id).execute()
        supabase.table("users").delete().eq("id", user_id).execute()
        supabase.auth.admin.delete_user(auth_id)


def test_authenticated_cannot_insert_user_links(
    db_client: DBClient, anon_client
) -> None:
    supabase = db_client.get_db()
    password = "Password123"
    email = f"rls-link-{uuid4().hex}@example.com"
    created = supabase.auth.admin.create_user(
        {
            "email": email,
            "password": password,
            "email_confirm": True,
        }
    )
    assert created.user is not None
    auth_id = created.user.id
    user_id = str(uuid7())

    try:
        supabase.rpc(
            "create_user_and_auth",
            {
                "p_user_id": user_id,
                "p_auth_id": auth_id,
                "p_email_encrypted": "rls-link",
                "p_email_hmac": f"rls-link-{uuid4().hex}",
                "p_provider": "EMAIL",
                "p_provider_id": None,
            },
        ).execute()
        signed_in = anon_client.auth.sign_in_with_password(
            {
                "email": email,
                "password": password,
            }
        )
        assert signed_in.user is not None

        try:
            response = (
                anon_client.table("user_links")
                .insert(
                    {
                        "id": str(uuid7()),
                        "user_id": user_id,
                        "type": "instagram",
                        "url": "https://sitio-de-phishing.example",
                        "sort_index": 0,
                    }
                )
                .execute()
            )
        except APIError:
            return
        assert not response.data
    finally:
        try:
            anon_client.auth.sign_out()
        except Exception:
            pass
        supabase.table("user_links").delete().eq("user_id", user_id).execute()
        supabase.table("auth").delete().eq("id", auth_id).execute()
        supabase.table("users").delete().eq("id", user_id).execute()
        supabase.auth.admin.delete_user(auth_id)


def test_anon_cannot_execute_update_profile(anon_client) -> None:
    try:
        anon_client.rpc(
            "update_profile",
            {
                "p_user_id": str(uuid7()),
                "p_name": "luna",
                "p_display_name": None,
                "p_avatar_url": None,
                "p_description": None,
                "p_updated_at": "2026-01-02T03:04:05+00:00",
                "p_links": [],
            },
        ).execute()
    except APIError:
        return
    raise AssertionError("anon no debería ejecutar update_profile")


def test_service_role_rpc_create_user_and_auth(db_client: DBClient) -> None:
    supabase = db_client.get_db()
    email = f"rls-{uuid4().hex}@example.com"
    created = supabase.auth.admin.create_user(
        {
            "email": email,
            "password": "Password123",
            "email_confirm": True,
        }
    )
    assert created.user is not None
    auth_id = created.user.id
    user_id = str(uuid7())

    try:
        supabase.rpc(
            "create_user_and_auth",
            {
                "p_user_id": user_id,
                "p_auth_id": auth_id,
                "p_email_encrypted": "rls-test",
                "p_email_hmac": f"rls-{uuid4().hex}",
                "p_provider": "EMAIL",
                "p_provider_id": None,
            },
        ).execute()

        auth_row = (
            supabase.table("auth").select("id,user_id").eq("id", auth_id).execute()
        )
        assert auth_row.data == [{"id": auth_id, "user_id": user_id}]
    finally:
        supabase.table("auth").delete().eq("id", auth_id).execute()
        supabase.table("users").delete().eq("id", user_id).execute()
        supabase.auth.admin.delete_user(auth_id)


def test_authenticated_cannot_read_auth_or_users(
    db_client: DBClient, anon_client
) -> None:
    supabase = db_client.get_db()
    password = "Password123"
    email = f"rls-own-{uuid4().hex}@example.com"
    created = supabase.auth.admin.create_user(
        {
            "email": email,
            "password": password,
            "email_confirm": True,
        }
    )
    assert created.user is not None
    auth_id = created.user.id
    user_id = str(uuid7())

    try:
        supabase.rpc(
            "create_user_and_auth",
            {
                "p_user_id": user_id,
                "p_auth_id": auth_id,
                "p_email_encrypted": "rls-own",
                "p_email_hmac": f"rls-own-{uuid4().hex}",
                "p_provider": "EMAIL",
                "p_provider_id": None,
            },
        ).execute()

        signed_in = anon_client.auth.sign_in_with_password(
            {
                "email": email,
                "password": password,
            }
        )
        assert signed_in.user is not None

        _assert_no_rows(lambda: anon_client.table("auth").select("id").execute())
        _assert_no_rows(lambda: anon_client.table("users").select("id").execute())
    finally:
        try:
            anon_client.auth.sign_out()
        except Exception:
            pass
        supabase.table("auth").delete().eq("id", auth_id).execute()
        supabase.table("users").delete().eq("id", user_id).execute()
        supabase.auth.admin.delete_user(auth_id)
