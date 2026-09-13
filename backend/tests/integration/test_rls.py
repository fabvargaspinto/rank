from uuid import uuid4

from postgrest.exceptions import APIError
from uuid6 import uuid7

from db.db_client import DBClient


def _assert_no_rows(execute):
    try:
        response = execute()
    except APIError:
        return
    assert response.data == [] or response.data is None


def test_anon_cannot_read_users(anon_client) -> None:
    _assert_no_rows(
        lambda: anon_client.table("users").select("id").limit(1).execute()
    )


def test_anon_cannot_read_auth(anon_client) -> None:
    _assert_no_rows(
        lambda: anon_client.table("auth").select("id").limit(1).execute()
    )


def test_anon_cannot_write_users(anon_client) -> None:
    user_id = str(uuid7())
    try:
        response = (
            anon_client.table("users")
            .insert({"id": user_id})
            .execute()
        )
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


def test_service_role_rpc_create_user_and_auth(db_client: DBClient) -> None:
    supabase = db_client.get_db()
    email = f"rls-{uuid4().hex}@example.com"
    created = supabase.auth.admin.create_user({
        "email": email,
        "password": "Password123",
        "email_confirm": True,
    })
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
            supabase.table("auth")
            .select("id,user_id")
            .eq("id", auth_id)
            .execute()
        )
        assert auth_row.data == [{"id": auth_id, "user_id": user_id}]
    finally:
        supabase.table("auth").delete().eq("id", auth_id).execute()
        supabase.table("users").delete().eq("id", user_id).execute()
        supabase.auth.admin.delete_user(auth_id)


def test_authenticated_reads_only_own_auth(db_client: DBClient, anon_client) -> None:
    supabase = db_client.get_db()
    password = "Password123"
    email = f"rls-own-{uuid4().hex}@example.com"
    created = supabase.auth.admin.create_user({
        "email": email,
        "password": password,
        "email_confirm": True,
    })
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

        signed_in = anon_client.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })
        assert signed_in.user is not None

        own = anon_client.table("auth").select("id").execute()
        assert [row["id"] for row in (own.data or [])] == [auth_id]

        own_users = anon_client.table("users").select("id").execute()
        assert [row["id"] for row in (own_users.data or [])] == [user_id]
    finally:
        try:
            anon_client.auth.sign_out()
        except Exception:
            pass
        supabase.table("auth").delete().eq("id", auth_id).execute()
        supabase.table("users").delete().eq("id", user_id).execute()
        supabase.auth.admin.delete_user(auth_id)
