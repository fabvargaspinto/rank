import pytest
from postgrest.exceptions import APIError
from uuid6 import uuid7

from core.shared.infrastructure.supabase_client import DBClient


def test_can_query_users_table(users_table: DBClient) -> None:
    response = users_table.get_db().table("users").select("id").limit(1).execute()

    assert response.data is not None
    assert isinstance(response.data, list)


def test_inserts_and_deletes_user(users_table: DBClient) -> None:
    user_id = str(uuid7())
    supabase = users_table.get_db()

    try:
        inserted = (
            supabase.table("users")
            .insert({"id": user_id, "name": "pytest-user"})
            .execute()
        )
        assert inserted.data[0]["id"] == user_id
        assert inserted.data[0]["name"] == "pytest-user"

        fetched = supabase.table("users").select("id,name").eq("id", user_id).execute()
        assert fetched.data == [{"id": user_id, "name": "pytest-user"}]
    finally:
        supabase.table("users").delete().eq("id", user_id).execute()


def test_luna_and_Luna_cannot_coexist(users_table: DBClient) -> None:
    first_id = str(uuid7())
    second_id = str(uuid7())
    supabase = users_table.get_db()

    try:
        supabase.table("users").insert({"id": first_id, "name": "luna"}).execute()

        with pytest.raises(APIError):
            supabase.table("users").insert({"id": second_id, "name": "Luna"}).execute()

        stored = (
            supabase.table("users")
            .select("id,name")
            .in_("id", [first_id, second_id])
            .execute()
        )
        assert stored.data == [{"id": first_id, "name": "luna"}]
    finally:
        supabase.table("users").delete().in_("id", [first_id, second_id]).execute()
